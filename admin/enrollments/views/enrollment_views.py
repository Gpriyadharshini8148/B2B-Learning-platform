from rest_framework import viewsets
from ..models.enrollment import Enrollment
from ..serializers.enrollment_serializer import EnrollmentSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class EnrollmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Enrollment.objects.all()
            
        return Enrollment.objects.filter(
            user__organization=self.request.user.organization
        )

    # Note: Enrollment model does not have an 'organization' field directly,
    # so we do not override perform_create to set organization.
