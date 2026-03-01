from rest_framework import viewsets, permissions
from ..models.organization import Organization
from ..serializers.organization_serializer import OrganizationSerializer
from ...access.permissions.tenant_permissions import IsSuperAdmin, IsOrganizationAdmin

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organizations.
    Super Admins: Full management.
    Org Admins: Can only see/update their own organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            return [IsSuperAdmin()]
        return [IsOrganizationAdmin()]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Organization.objects.all()
        return Organization.objects.filter(id=user.organization_id)
