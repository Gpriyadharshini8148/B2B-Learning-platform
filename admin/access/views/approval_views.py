from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole
from admin.access.authentication.keycloak_manager import register_user_with_role
from django.core import signing

from admin.access.authentication.keycloak_manager import create_organization_group, setup_base_roles
from django.contrib.auth.hashers import make_password

class OrgApprovalView(views.APIView):
    permission_classes = [permissions.AllowAny] 

    @extend_schema(responses={200: dict, 400: dict})
    def get(self, request, token, action):

        

        try:
            # Token expires after 7 days
            data = signing.loads(token, max_age=86400 * 7)
        except signing.BadSignature:
            return Response({"error": "Invalid or expired approval link"}, status=status.HTTP_400_BAD_REQUEST)

        org_name = data.get('name')
        subdomain = data.get('subdomain')
        email = data.get('email')
        password = data.get('password')

        if action == 'accept':
            # Check if subdomain or email were taken while the request was pending
            if Organization.objects.filter(subdomain=subdomain).exists():
                return Response({"error": "This subdomain has already been registered by another organization."}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                 return Response({"error": "This email is already in use by another user."}, status=status.HTTP_400_BAD_REQUEST)

            # Insert into the database NOW
            org = Organization.objects.create(
                name=org_name,
                subdomain=subdomain,
                approval_status='approved',
                is_active=True,
                is_verified=True
            )

            user = User.objects.create(
                organization=org,
                email=email,
                first_name="Admin",
                last_name=org_name,
                password_hash=make_password(password),
                is_active=True,
                is_verified=True,
                approval_status='approved'
            )

            # Assign roles
            role, _ = Role.objects.get_or_create(
                name='organization_admin',
                organization=org,
                defaults={'description': 'System-assigned Organization Admin'}
            )
            UserRole.objects.get_or_create(user=user, role=role)

            # Setup Keycloak
            setup_base_roles()
            create_organization_group(subdomain)
            register_user_with_role(
                email=user.email,
                role_name="organization_admin",
                organization_subdomain=org.subdomain,
                password=password
            )

            return Response({"message": f"Organization '{org_name}' successfully created, approved, and registered in Keycloak."}, status=status.HTTP_200_OK)

        elif action == 'reject':
            return Response({"message": f"Organization request for '{org_name}' has been rejected. No database records were created."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class UserApprovalView(views.APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: dict, 400: dict, 404: dict})
    def get(self, request, token, action):
        try:
            user = User.objects.get(approval_token=token)

            if user.approval_status != 'pending':
                return Response({"message": f"User already {user.approval_status}"}, status=status.HTTP_400_BAD_GATEWAY)

            if action == 'accept':
                user.approval_status = 'approved'
                user.is_active = True
                user.is_verified = True
                user.save()
                
                # Assign default 'learner' role if no roles exist
                if not user.user_roles.exists():
                    role, _ = Role.objects.get_or_create(
                        name='learner',
                        organization=user.organization,
                        defaults={'description': 'System-assigned Learner'}
                    )
                    UserRole.objects.get_or_create(user=user, role=role)
                
                return Response({"message": "User account approved successfully. You can now login."}, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                user.approval_status = 'rejected'
                user.is_active = False
                user.save()
                return Response({"message": f"Account approval rejected by {user.email}"}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
