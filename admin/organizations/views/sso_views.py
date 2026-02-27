from rest_framework import viewsets
from ..models.organization_sso import OrganizationSSO
from ..serializers.sso_serializer import OrganizationSSOSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class SSOViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = OrganizationSSO
    queryset = OrganizationSSO.objects.all()
    serializer_class = OrganizationSSOSerializer
