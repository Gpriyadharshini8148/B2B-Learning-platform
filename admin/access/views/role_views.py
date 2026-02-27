from rest_framework import viewsets
from ..models.role import Role
from ..serializers.role_serializer import RoleSerializer
from ..permissions.tenant_permissions import TenantSafeViewSetMixin

class RoleViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Role
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
