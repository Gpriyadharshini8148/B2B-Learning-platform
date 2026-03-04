from rest_framework import viewsets, permissions
from admin.access.models import Section
from admin.users.serializers.section_serializer import SectionDetailSerializer

class UserSectionViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner‑side Read-Only view for Section."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SectionDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Section.objects.filter(organization=org)
