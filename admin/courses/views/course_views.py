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

        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return queryset
        
        # Courses for an organization are linked via OrganizationCourse
        # Filtering for courses mapped to the user's organization
        return queryset.filter(organization_courses__organization=user.organization)

    def perform_create(self, serializer):
        course = serializer.save(instructor=self.request.user)
        
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

        # Automatically map the course to the admin's organization
        if not self.request.user.is_superuser and getattr(self.request.user, 'email', '') != super_admin_email:
            from ..models.organization_course import OrganizationCourse
            OrganizationCourse.objects.create(
                organization=self.request.user.organization,
                course=course
            )
