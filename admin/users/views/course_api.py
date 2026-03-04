from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models.course import Course
from admin.users.serializers.course_serializer import CourseDetailSerializer

class StudentCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/users/courses/{id}
    Browse courses available to the student's organization.
    """
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        # Access courses that belong specifically to this organization
        return Course.objects.filter(
            organization=organization,
            is_published=True,
            is_deleted=False
        )

    @action(detail=True, methods=['get'])
    def instructor(self, request, pk=None):
        course = self.get_object()
        instructor = course.instructor
        if not instructor:
            return Response({"message": "No instructor assigned to this course"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({
            "id": instructor.id,
            "name": f"{instructor.first_name} {instructor.last_name}".strip() or instructor.email,
            "email": instructor.email
        })

    @action(detail=True, methods=['get'])
    def thumbnail(self, request, pk=None):
        course = self.get_object()
        return Response({
            "thumbnail_url": course.thumbnail_url
        })
