from rest_framework import viewsets
from ..models.payment import Payment
from ..serializers.payment_serializer import PaymentSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class PaymentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Payment.objects.all()
            
        return Payment.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )
