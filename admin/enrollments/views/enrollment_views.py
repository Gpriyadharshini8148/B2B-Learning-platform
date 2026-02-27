from rest_framework import viewsets
from ..models.enrollment import Enrollment
from ..serializers.enrollment_serializer import EnrollmentSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class EnrollmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Enrollment
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
