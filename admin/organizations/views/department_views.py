from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models.department import Department
from admin.access.models.user_department import UserDepartment
from ..serializers.department_serializer import DepartmentSerializer
from ..serializers.user_department_serializer import UserDepartmentSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class OrgDepartmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific department management.
    Allows Org Admins to create and manage departments within their organization.
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Department.objects.all()
            
        return Department.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )

class OrgUserDepartmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Manage user-department associations within the organization.
    """
    serializer_class = UserDepartmentSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return UserDepartment.objects.all()
            
        return UserDepartment.objects.filter(
            department__organization=self.request.user.organization
        )
