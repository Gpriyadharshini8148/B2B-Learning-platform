from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import transaction
from drf_spectacular.utils import extend_schema
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.authentication.serializers import OrganizationSignupSerializer, LearnerSignupSerializer

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
            
        email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        org_name = request.data.get('organization_name')
        subdomain = request.data.get('subdomain')

        if not all([email, password, org_name, subdomain]):
            return Response({"error": "Fields 'username', 'password', 'organization_name', and 'subdomain' are required."}, 
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
        # Prevent the user creation signal from taking over
        # We handle notification manually to Super Admin below
        user._is_signup = False 
        user._skip_signal = True
        user.save()

        # 3. Notify Super Admin about the new Organization request
        super_admin_email = settings.EMAIL_HOST_USER
        
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/reject/"

        subject = f"NEW REGISTRATION REQUEST: {org.name}"
        message = (
            f"Hello Super Admin,\n\n"
            f"A new organization has requested to join:\n\n"
            f"Organization: {org.name}\n"
            f"Subdomain: {org.subdomain}\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        
        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                print(f"Failed to send email to Super Admin: {e}")
                
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, super_admin_email)

        return Response({
            "message": "Registration request sent to the Super Admin for approval.",
        }, status=status.HTTP_200_OK)

class LearnerSignupView(views.APIView):
    """
    Public API for Learners to register.
    Creates a pending user and sends an approval request to the Organization Admin.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=LearnerSignupSerializer)
    def post(self, request):
        serializer = LearnerSignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        email = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')
        subdomain = request.data.get('organization_subdomain')

        if not all([email, password, subdomain]):
            return Response({"error": "Fields 'username', 'password', and 'organization_subdomain' are required."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            org = Organization.objects.get(subdomain=subdomain)
        except Organization.DoesNotExist:
            return Response({"error": "The specified organization does not exist."}, status=status.HTTP_404_NOT_FOUND)

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.approval_status == 'pending':
                return Response({"error": "This learner is already registered and pending approval by the Organization Admin."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Create User (Pending Approval)
        user = User(
            organization=org,
            email=email,
            password_hash=make_password(password),
            is_active=False,
            approval_status='pending'
        )
        user._is_signup = True
        user._skip_signal = True # Bypass signal to send email directly with password
        user.save()

        # Find the admin of this organization (usually the owner/first user)
        admin_user = User.objects.filter(organization=org).exclude(id=user.id).first()
        recipient_email = admin_user.email if admin_user else settings.EMAIL_HOST_USER

        accept_link = f"http://localhost:8000/api/bulk-cms/approve/user/{user.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/user/{user.approval_token}/reject/"
        
        subject = "New Learner Signup: Approval Required"
        message = (
            f"A new learner has requested to join your organization '{org.name}'.\n\n"
            f"Details:\n"
            f"- Username / Email: {email}\n"
            f"- Password: {password}\n"
            f"- Organization ID: {org.id}\n\n"
            f"Please click the link below to approve or reject this request:\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )
        
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        
        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                print(f"Failed to send email to Org Admin: {e}")
                
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, recipient_email)

        return Response({
            "message": "Registration request sent to the Organization Admin for approval.",
        }, status=status.HTTP_200_OK)
