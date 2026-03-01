from rest_framework import viewsets
from ..models.organization_sso import OrganizationSSO
from ..serializers.sso_serializer import OrganizationSSOSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class SSOViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = OrganizationSSOSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return OrganizationSSO.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )
