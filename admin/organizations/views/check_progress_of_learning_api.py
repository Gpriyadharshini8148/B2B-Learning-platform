from django.conf import settings
from rest_framework import viewsets
from admin.access.models.course_progress import CourseProgress
from admin.organizations.serializers.course_progress_serializer import CourseProgressSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class OrgCheckProgressOfLearningViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific view to check and audit the progress of learners.
    This provides detailed visibility into how students are progressing through courses.
    """
    serializer_class = CourseProgressSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return CourseProgress.objects.all()
            
        return CourseProgress.objects.filter(
            enrollment__user__organization=user.organization
        ).select_related('enrollment__user', 'enrollment__course')
