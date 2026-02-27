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

    def perform_create(self, serializer):
        # Automatically assign the organization if the creator is an Org Admin
        if not self.request.user.is_superuser:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()
