from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models.user import User
from admin.access.serializers.user_serializer import UserSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class OrgManageUserViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Org Admins to manage users within their organization.
    Ensures tenant isolation and role-based access.
    """
    serializer_class = UserSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return User.objects.all()
            
        if hasattr(user, 'organization') and user.organization:
            return User.objects.filter(organization=user.organization)
        return User.objects.none()

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Action to deactivate a user.
        """
        user_to_deactivate = self.get_object()
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        return Response({
            "message": f"User {user_to_deactivate.email} has been deactivated."
        }, status=status.HTTP_200_OK)
