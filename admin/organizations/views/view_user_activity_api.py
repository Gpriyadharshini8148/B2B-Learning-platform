from rest_framework import viewsets, permissions
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin
from admin.access.models.audit_log import AuditLog
from rest_framework import serializers

class OrgAuditLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_email', 'action', 'entity_type', 'entity_id', 'metadata', 'created_at']

class OrgUserActivityViewSet(TenantSafeViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Org Admins to monitor actions performed by their users.
    """
    serializer_class = OrgAuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    queryset = AuditLog.objects.all().order_by('-created_at')

    def get_queryset(self):
        return AuditLog.objects.filter(organization=self.request.user.organization)
