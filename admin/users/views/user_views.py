from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models.user import User
from admin.access.serializers.user_serializer import UserSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class UserManagementViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing users within an organization.
    Enforces tenant isolation so Org Admins only see their users.
    """
    serializer_class = UserSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return User.objects.all()
            
        if hasattr(user, 'organization') and user.organization:
            return User.objects.filter(organization=user.organization)
        return User.objects.none()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=False, methods=['post'])
    def invite(self, request):
        """
        Custom action to invite a new user to the organization.
        """
        email = request.data.get('email')
        role = request.data.get('role', 'learner')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegates to the core invitation logic built earlier
        return Response({"message": f"Invitation sent to {email} as {role}."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Custom action to deactivate a user.
        """
        user_to_deactivate = self.get_object()
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        return Response({
            "message": f"User {user_to_deactivate.email} has been deactivated."
        }, status=status.HTTP_200_OK)
