from rest_framework import viewsets
from ..models.organization_domain import OrganizationDomain
from ..serializers.domain_serializer import OrganizationDomainSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class DomainViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = OrganizationDomain
    queryset = OrganizationDomain.objects.all()
    serializer_class = OrganizationDomainSerializer
