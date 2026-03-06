import logging
from rest_framework import views, status, permissions

logger = logging.getLogger(__name__)
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.authentication.serializers import OrganizationSignupSerializer, UserSignupSerializer
from admin.access.authentication.keycloak_manager import create_organization_group, register_user_with_role
from django.utils import timezone
import datetime
import string
import random

class OrganizationSignupView(views.APIView):
    """
    Public API for Organizations to register.
    Creates a pending user/org and directly sends an approval request to the Super Admin.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OrganizationSignupSerializer, responses={201: dict, 400: dict})
    def post(self, request):
        serializer = OrganizationSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        email = request.data.get('admin_email')
        password = request.data.get('password') # Note: Assuming password must still be passed 
        
        # If no password provided, generate a secure temporary one
        if not password:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + "A1!"
            
        org_name = request.data.get('name')
        subdomain = request.data.get('subdomain')

        if not all([email, org_name, subdomain]):
            return Response({"error": "Fields 'admin_email', 'name', and 'subdomain' are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        if Organization.objects.filter(subdomain=subdomain).exists():
            return Response({"error": "The subdomain is already in use."}, status=status.HTTP_400_BAD_REQUEST)

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.approval_status == 'pending':
                return Response({"error": "This organization is already registered and pending approval by the Super Admin."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        from django.core import signing
        from concurrent.futures import ThreadPoolExecutor

        # Package the organization data securely (no DB insert yet)
        data = {
            'name': org_name,
            'subdomain': subdomain,
            'email': email,
            'password': password
        }
        token = signing.dumps(data)

        # Send approval email directly from this view since we aren't using signals
        subject = f"NEW REGISTRATION REQUEST: {org_name}"
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/org/{token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/org/{token}/reject/"

        message = (
            f"Hello Super Admin,\n\n"
            f"A new organization has requested to join:\n\n"
            f"Organization: {org_name}\n"
            f"Subdomain: {subdomain}\n"
            f"Admin Email: {email}\n\n"
            f"Click here to Accept and Provision: {accept_link}\n"
            f"Click here to Reject: {reject_link}\n"
        )

        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                print(f"Failed to send email to Super Admin: {e}")

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, settings.EMAIL_HOST_USER)

        return Response({
            "message": "Organization registration request sent successfully! The Super Admin will review and approve your organization within 24 hours. You will receive an email confirmation once approved.",
            "status": "pending_approval"
        }, status=status.HTTP_201_CREATED)


class UserSignupView(views.APIView):
    """
    Public API for Users to register.
    Creates a pending user and sends an approval request to the Organization Admin.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserSignupSerializer, responses={201: dict, 200: dict, 400: dict})
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        subdomain = request.data.get('organization_subdomain', '').strip()

        if not all([email, password]):
            return Response({"error": "Fields 'username' (or 'email') and 'password' are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        org = None
        if subdomain:
            logger.info(f"UserSignup: Looking for organization with subdomain: {subdomain}")
            try:
                org = Organization.objects.get(subdomain__iexact=subdomain)
                logger.info(f"UserSignup: Found organization: {org.name}")
            except Organization.DoesNotExist:
                all_orgs = Organization.objects.all().values_list('subdomain', flat=True)
                logger.warning(f"UserSignup: Organization not found. Available: {list(all_orgs)}")
                return Response({"error": "The specified organization does not exist."}, status=status.HTTP_404_NOT_FOUND)

        otp = str(random.randint(100000, 999999))

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.approval_status == 'pending':
                return Response({"error": "This user is already registered and pending approval by the Organization Admin."}, status=status.HTTP_400_BAD_REQUEST)
            if existing_user.approval_status != 'pending_otp':
                return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check 2 min rate limit
           
            if existing_user.otp_created_at:
                time_diff = timezone.now() - existing_user.otp_created_at
                if time_diff < datetime.timedelta(minutes=2):
                    seconds_left = int(120 - time_diff.total_seconds())
                    return Response({
                        "error": f"OTP already shared with your mail. Please wait {seconds_left} seconds before requesting a new one."
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            # Update existing pending_otp user with new OTP and optionally new password/org
            existing_user.otp = otp
            existing_user.otp_created_at = timezone.now()
            existing_user.password_hash = make_password(password)
            existing_user.organization = org
            existing_user._is_signup = True
            existing_user.save()

            # Resync keycloak password if they changed it on second attempt
            register_user_with_role(
                email=email,
                role_name="organization_user",
                organization_subdomain=org.subdomain if org else None,
                password=password,
                enabled=False
            )
            
            return Response({
                "message": "otp shared with your email",
            }, status=status.HTTP_200_OK)

        # 1. Ensure Keycloak Group exists for this organization
        if org:
            create_organization_group(org.subdomain)

        # 2. Keycloak Registration (Disabled until OTP verification)
        # We must do this now while we still have access to the plain text password.
        register_user_with_role(
            email=email,
            role_name="organization_user",
            organization_subdomain=org.subdomain if org else None,
            password=password,
            enabled=False # User cannot login until OTP is verified
        )

        # 3. Create User (Pending OTP)
        user = User(
            organization=org,
            email=email,
            password_hash=make_password(password),
            is_active=False,
            approval_status='pending_otp',
            otp=otp,
            otp_created_at=timezone.now()
        )
        user._is_signup = True
        user.save()

        # 4. Send OTP email
        from concurrent.futures import ThreadPoolExecutor
        def _send_otp_email(recipient, otp_code):
            try:
                send_mail(
                    subject="Your OTP code",
                    message=(
                        f"Hello,\n\n"
                        f"Your One-Time Password (OTP) for signup is:\n\n"
                        f"  {otp_code}\n\n"
                        f"This OTP is valid for 10 minutes. Do not share it with anyone."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send OTP email to {recipient}: {e}")

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(_send_otp_email, email, otp)

        return Response({
            "message": f"An OTP has been sent to {email}. Please verify to complete signup.",
        }, status=status.HTTP_201_CREATED)
