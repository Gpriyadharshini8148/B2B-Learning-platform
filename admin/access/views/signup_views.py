from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from drf_spectacular.utils import extend_schema
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.authentication.serializers import OrganizationSignupSerializer, UserSignupSerializer
from django.utils import timezone
import datetime
class OrganizationSignupView(views.APIView):
    """
    Public API for Organizations to register.
    Creates a pending user/org and directly sends an approval request to the Super Admin.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=OrganizationSignupSerializer)
    @transaction.atomic
    def post(self, request):
        serializer = OrganizationSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        email = request.data.get('admin_email')
        password = request.data.get('password') # Note: Assuming password must still be passed 
        
        # If no password provided, generate a secure temporary one
        if not password:
            import string
            import random
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

        # 1. Create Organization (Pending Approval)
        org = Organization.objects.create(
            name=org_name,
            subdomain=subdomain,
            approval_status='pending',
            is_active=False
        )

        # 2. Create User (Pending Approval)
        user = User(
            organization=org,
            email=email,
            password_hash=make_password(password),
            is_active=False,
            approval_status='pending'
        )
        user._is_org_signup = True 
        user.save()

        return Response({
            "message": "Registration request sent to the Super Admin for approval.",
        }, status=status.HTTP_200_OK)

class UserSignupView(views.APIView):
    """
    Public API for Users to register.
    Creates a pending user and sends an approval request to the Organization Admin.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=UserSignupSerializer)
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        subdomain = request.data.get('organization_subdomain')

        if not all([email, password]):
            return Response({"error": "Fields 'username' (or 'email') and 'password' are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        org = None
        if subdomain:
            try:
                org = Organization.objects.get(subdomain=subdomain)
            except Organization.DoesNotExist:
                return Response({"error": "The specified organization does not exist."}, status=status.HTTP_404_NOT_FOUND)

        import random
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
            
            return Response({
                "message": "otp shared with your email",
            }, status=status.HTTP_200_OK)

        # 1. Create User (Pending OTP)
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
        # Do not skip signal - the signal will now send the OTP email!
        user.save()

        return Response({
            "message": "otp shared with your email",
        }, status=status.HTTP_200_OK)
