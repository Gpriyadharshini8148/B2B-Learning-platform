from rest_framework import viewsets, permissions
from admin.access.models import Course
from admin.users.serializers.course_serializer import CourseDetailSerializer

class UserCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner side Read-Only view for Course."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Course.objects.filter(organization=org)
