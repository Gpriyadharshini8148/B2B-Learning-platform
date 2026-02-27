from rest_framework import viewsets
from ..models.section import Section
from ..serializers.section_serializer import SectionSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class SectionViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Section
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
