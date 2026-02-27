from rest_framework import viewsets
from ..models.department import Department
from ..serializers.department_serializer import DepartmentSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class DepartmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Department
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
