from rest_framework import viewsets, permissions
from admin.access.permissions.tenant_permissions import IsOrganizationAdmin
from admin.organizations.models.invitation import Invitation
from rest_framework import serializers

class PendingInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'role', 'token', 'created_at', 'expires_at', 'is_used']

class OrgReviewPendingInvitesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Org Admins to monitor invitations that haven't been accepted yet.
    """
    serializer_class = PendingInviteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        return Invitation.objects.filter(
            organization=self.request.user.organization,
            is_used=False
        ).order_by('-created_at')
