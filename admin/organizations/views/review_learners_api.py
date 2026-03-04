from rest_framework import viewsets, permissions
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin
from admin.access.models.user import User
from admin.access.serializers.user_serializer import UserSerializer

class OrgReviewLearnersViewSet(TenantSafeViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Org Admins to see all active learners in their organization.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    queryset = User.objects.all()

    def get_queryset(self):
        # Filter for users in this org that are NOT admins (learners)
        # Note: Depending on role management, this might filter by role name.
        return User.objects.filter(
            organization=self.request.user.organization
        ).exclude(
            user_roles__role__name__in=['organization_admin', 'admin', 'staff']
        ).distinct()
