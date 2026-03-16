from django.conf import settings
from rest_framework import viewsets, permissions
from ..models.user import User
from ..serializers.user_serializer import UserSerializer
from ..permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class UserViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing Users.
    Super Admins: Can see all users.
    Org Admins: Can see only their organization's users.
    """
    model = User
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        # Exclude super admins from appearing in generic user views
        return qs.exclude(email=super_admin_email).exclude(is_superuser=True)

    def perform_create(self, serializer):
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        # Automatically assign the organization if the creator is an Org Admin
        if not self.request.user.is_superuser and getattr(self.request.user, 'email', '') != super_admin_email:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()
