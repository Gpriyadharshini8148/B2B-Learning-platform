from rest_framework import viewsets, permissions
from ..models.course import Course
from ..serializers.course_serializer import CourseSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class CourseViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Course Management.
    Super Admins: All courses.
    Org Admins: Only courses belonging to their organization via OrganizationCourse mapping.
    """
    model = Course
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            return queryset
        
        # Courses for an organization are linked via OrganizationCourse
        # Filtering for courses mapped to the user's organization
        return queryset.filter(organization_courses__organization=user.organization)

    def perform_create(self, serializer):
        course = serializer.save(instructor=self.request.user)
        
        # Automatically map the course to the admin's organization
        if not self.request.user.is_superuser:
            from ..models.organization_course import OrganizationCourse
            OrganizationCourse.objects.create(
                organization=self.request.user.organization,
                course=course
            )
