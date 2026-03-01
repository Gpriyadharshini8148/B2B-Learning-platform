from rest_framework import viewsets
from ..models.certificate import Certificate
from ..serializers.certificate_serializer import CertificateSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class CertificateViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Certificate.objects.filter(enrollment__status='completed')
            
        return Certificate.objects.filter(
            enrollment__user__organization=self.request.user.organization,
            enrollment__status='completed'
        )
