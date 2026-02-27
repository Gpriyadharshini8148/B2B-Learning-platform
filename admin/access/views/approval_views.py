from rest_framework import views, status, permissions
from rest_framework.response import Response
from admin.organizations.models.organization import Organization
from admin.access.models.user import User

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
                org.users.filter(approval_status='pending').update(
                    is_active=True, 
                    is_verified=True,
                    approval_status='approved'
                )
                
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
                return Response({"message": "User account approved successfully. You can now login."}, status=status.HTTP_200_OK)
            
            elif action == 'reject':
                user.approval_status = 'rejected'
                user.is_active = False
                user.save()
                return Response({"message": f"Account approval rejected by {user.email}"}, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
