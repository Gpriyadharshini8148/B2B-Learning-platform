from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core import signing
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from admin.access.models.user import User
from admin.access.authentication.keycloak_manager import (
    get_keycloak_admin, 
    setup_base_roles, 
    create_organization_group, 
    register_user_with_role
)
from admin.organizations.models.organization import Organization
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole

class ResetPasswordView(views.APIView):
    """
    API for users to set or reset their password using a signed token.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: dict})
    def get(self, request):
        """
        Validates the token from the URL and provides instructions.
        """
        token = request.query_params.get('token')
        if not token:
            return Response({"error": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Try parsing as a provisioning token (dict) first
            try:
                data = signing.loads(token, max_age=86400)
                if isinstance(data, dict):
                    email = data.get('email')
                    return Response({
                        "message": f"Welcome! Setup your new account for '{data.get('name')}'.",
                        "instructions": "Please send a POST request with your desired password to finalize setup.",
                        "email": email,
                        "type": "new_account_setup"
                    }, status=status.HTTP_200_OK)
            except Exception:
                pass

            # Fallback to standard TimestampSigner
            signer = TimestampSigner()
            email = signer.unsign(token, max_age=86400)
            return Response({
                "message": f"Token is valid for {email}.",
                "instructions": "Please send a POST request to this same URL with 'token' and 'password' in the body to set your new password.",
                "token": token
            }, status=status.HTTP_200_OK)
        except SignatureExpired:
            return Response({"error": "Password reset link has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(request={'token': str, 'password': str}, responses={200: dict})
    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')

        if not token or not password:
            return Response({"error": "token and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Unsign and Detect Token Type
        provisioning_data = None
        email = None
        
        try:
            # Check for provisioning token
            try:
                data = signing.loads(token, max_age=86400)
                if isinstance(data, dict):
                    provisioning_data = data
                    email = data.get('email')
            except Exception:
                pass

            if not email:
                signer = TimestampSigner()
                email = signer.unsign(token, max_age=86400)
                
        except SignatureExpired:
            return Response({"error": "Link has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. JIT Database Creation (if provisioning)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            if provisioning_data:
                # Create the Organization first
                
                org, _ = Organization.objects.get_or_create(
                    subdomain=provisioning_data['subdomain'],
                    defaults={
                        'name': provisioning_data['name'],
                        'is_active': True,
                        'is_verified': True,
                        'approval_status': 'approved'
                    }
                )
                
                # Create the User
                user = User(
                    email=email,
                    first_name="Admin",
                    last_name=provisioning_data['name'],
                    organization=org,
                    is_active=True,
                    is_verified=True,
                    approval_status='approved'
                )
                user._skip_signal = True
                user.save()
                
                # Assign Role
                admin_role, _ = Role.objects.get_or_create(
                    name="organization_admin",
                    organization=org
                )
                UserRole.objects.get_or_create(user=user, role=admin_role)
            else:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Set the new password in the Django Database
        user.password_hash = make_password(password)
        user._skip_signal = True
        user.save()

        # Update or Create User in Keycloak (JIT Provisioning)
        try:
            # 1. Ensure basics are ready
            setup_base_roles()
            if user.organization:
                create_organization_group(user.organization.subdomain)

            # 2. Get the role from our DB to sync
            user_role = UserRole.objects.filter(user=user).select_related('role').first()
            role_name = user_role.role.name if user_role else 'organization_user'

            # 3. Synchronize with Keycloak
            kc_success, kc_msg = register_user_with_role(
                email=email,
                role_name=role_name,
                organization_subdomain=user.organization.subdomain if user.organization else None,
                password=password,
                enabled=True
            )
            
            if not kc_success:
                 return Response({"error": f"Failed to sync with Keycloak: {kc_msg}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({"error": f"Critical Keycloak Sync Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Password successfully set/reset. You can now login."}, status=status.HTTP_200_OK)
