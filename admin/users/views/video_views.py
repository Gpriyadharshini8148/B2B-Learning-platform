from rest_framework import viewsets, permissions
from admin.access.models import Video
from admin.users.serializers.video_serializer import VideoDetailSerializer

class UserVideoViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner side Read-Only view for Video."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VideoDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Video.objects.filter(organization=org)
