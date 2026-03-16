from django.conf import settings
from rest_framework import viewsets
from admin.access.models.category import Category
from ..serializers.category_serializer import CategorySerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class OrgCategoryViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsOrgAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Category.objects.all()
            
        return Category.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )
