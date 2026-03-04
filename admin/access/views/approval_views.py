from rest_framework import views, status, permissions
from rest_framework.response import Response
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole

class OrgApprovalView(views.APIView):
    permission_classes = [permissions.AllowAny] # Links are public

    def get(self, request, token, action):
        try:
            org = Organization.objects.get(approval_token=token)
            
            if org.approval_status != 'pending':
                return Response({"message": f"Organization already {org.approval_status}"}, status=status.HTTP_400_BAD_GATEWAY)

            if action == 'accept':
                org.approval_status = 'approved'
                org.is_active = True
                org.is_verified = True
                org.save()
                
                # Activate the pending users inside this organization (e.g. the admin who registered)
                pending_users = org.users.filter(approval_status='pending')
                
                # Fetch or create the organization_admin role
                role, _ = Role.objects.get_or_create(
                    name='organization_admin',
                    organization=org,
                    defaults={'description': 'System-assigned Organization Admin'}
                )
                
                for user in pending_users:
                    user.is_active = True
                    user.is_verified = True
                    user.approval_status = 'approved'
                    user.save()
                    
                    # Assign the role
                    UserRole.objects.get_or_create(user=user, role=role)
                
                return Response({"message": "Organization approved successfully. You can now login."}, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                org.approval_status = 'rejected'
                org.is_active = False
                org.save()
                return Response({"message": f"Account approval rejected by {org.name}"}, status=status.HTTP_200_OK)
            
        except Organization.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)

class UserApprovalView(views.APIView):
    permission_classes = [permissions.AllowAny]

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
