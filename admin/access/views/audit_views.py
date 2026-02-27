from rest_framework import viewsets, permissions
from ..models.audit_log import AuditLog
from ..serializers.audit_serializer import AuditLogSerializer
from ..permissions.tenant_permissions import TenantSafeViewSetMixin

class AuditLogViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = AuditLog
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    http_method_names = ['get', 'head', 'options'] # Read only
