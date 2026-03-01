from rest_framework import viewsets
from ..models.audit_log import AuditLog
from ..serializers.audit_serializer import AuditLogSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class AuditViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return AuditLog.objects.all()
            
        return AuditLog.objects.filter(
            organization=self.request.user.organization
        )
