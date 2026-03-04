from rest_framework import viewsets, permissions
from admin.access.models import Lesson
from admin.users.serializers.lesson_serializer import LessonDetailSerializer

class UserLessonViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner‑side Read-Only view for Lesson."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LessonDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Lesson.objects.filter(organization=org)
