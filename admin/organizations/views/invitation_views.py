import logging
from rest_framework import views, status, permissions, serializers
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema
from admin.organizations.serializers.invitation_serializer import InviteUserSerializer, AcceptInvitationSerializer
from admin.organizations.models.invitation import Invitation
from admin.access.models.user import User
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole
from admin.access.authentication.keycloak_manager import (
    register_user_with_role,
    create_organization_group,
    setup_base_roles
)
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class OrgInviteNewUserView(views.APIView):
    """
    API for Organization Admins to invite a user to their organization.
    Sends an invitation email with a signed secure link.
    No DB entry for the invited user is made until they accept.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=InviteUserSerializer,
        responses={200: serializers.DictField()}
    )
    def post(self, request):
        admin_user = request.user
        if not admin_user.organization:
            return Response(
                {"error": "You do not belong to any organization."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = request.data.get('email')
        role_name = request.data.get('role', 'organization_user')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already in system
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email is already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        org = admin_user.organization

        # Build or refresh an Invitation record (for tracking purposes)
        invitation, _ = Invitation.objects.update_or_create(
            email=email,
            organization=org,
            defaults={'is_used': False, 'role': role_name}
        )

        # Build a signed token that encodes the invitation details securely
        from django.core import signing
        token_data = {
            'invitation_id': str(invitation.token),   # UUID from the DB record
            'email': email,
            'org_id': org.pk,
            'role': role_name,
        }
        signed_token = signing.dumps(token_data)

        base_url = request.build_absolute_uri('/').rstrip('/')
        accept_url = f"{base_url}/api/organizations/accept-invite/?token={signed_token}"

        subject = f"You're invited to join {org.name}!"
        message = (
            f"Hello,\n\n"
            f"You have been invited by {admin_user.email} to join "
            f"'{org.name}' as a '{role_name}'.\n\n"
            f"Click the link below to set up your account:\n"
            f"{accept_url}\n\n"
            f"This link will expire in 7 days.\n\n"
            f"If you did not expect this invitation, you can ignore this email."
        )

        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                logger.error(f"Failed to send invitation email to {recipient}: {e}")

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, email)

        return Response({
            "message": f"Invitation sent to {email}.",
            "invite_url": accept_url,   # Also returned for testing
        }, status=status.HTTP_200_OK)


class AcceptInvitationView(views.APIView):
    """
    API for users to accept an invitation and complete their account setup.
    Provisions the user in both Django and Keycloak.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=AcceptInvitationSerializer, responses={201: dict})
    def post(self, request):
        from django.core import signing
        from admin.organizations.models.organization import Organization

        token = request.data.get('token') or request.query_params.get('token')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        password = request.data.get('password')

        if not token or not password:
            return Response(
                {"error": "'token' and 'password' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Decode the signed token (max 7 days)
        try:
            data = signing.loads(token, max_age=86400 * 7)
        except signing.SignatureExpired:
            return Response(
                {"error": "This invitation link has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except signing.BadSignature:
            return Response(
                {"error": "Invalid invitation link."},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = data.get('email')
        org_id = data.get('org_id')
        role_name = data.get('role', 'organization_user')
        invitation_token = data.get('invitation_id')

        # Fetch the Invitation DB record to check is_used / expiry
        try:
            invitation = Invitation.objects.get(token=invitation_token)
        except Invitation.DoesNotExist:
            return Response({"error": "Invitation not found."}, status=status.HTTP_400_BAD_REQUEST)

        if not invitation.is_valid():
            return Response(
                {"error": "Invitation has already been used or has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email is already registered."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            org = Organization.objects.get(pk=org_id)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found."}, status=status.HTTP_400_BAD_REQUEST)

        # --- 1. Create User in Django DB ---
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=make_password(password),
            organization=org,
            is_active=True,
            is_verified=True,
            approval_status='approved',
        )

        # --- 2. Assign Django Role ---
        role, _ = Role.objects.get_or_create(
            name=role_name,
            organization=org,
            defaults={'description': f'System role: {role_name}'}
        )
        UserRole.objects.get_or_create(user=user, role=role)

        # --- 3. Keycloak Provisioning ---
        setup_base_roles()
        create_organization_group(org.subdomain)
        kc_success, kc_msg = register_user_with_role(
            email=email,
            role_name=role_name,
            organization_subdomain=org.subdomain,
            password=password,
            enabled=True  # User is immediately active — they clicked an invitation link
        )
        if not kc_success:
            logger.warning(f"Keycloak provisioning warning for {email}: {kc_msg}")

        # --- 4. Mark invitation as used ---
        invitation.is_used = True
        invitation.save()

        return Response({
            "message": (
                f"Welcome! Your account has been created and linked to '{org.name}'. "
                "You can now login."
            ),
            "email": email,
            "organization": org.name,
            "role": role_name,
        }, status=status.HTTP_201_CREATED)
