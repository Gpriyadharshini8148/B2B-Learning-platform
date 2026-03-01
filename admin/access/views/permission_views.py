from rest_framework import viewsets
from ..models.permission import Permission
from ..serializers.permission_serializer import PermissionSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class PermissionViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = PermissionSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        return Permission.objects.all()
