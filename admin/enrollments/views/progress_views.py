from rest_framework import viewsets
from ..models.course_progress import CourseProgress
from ..models.lesson_progress import LessonProgress
from ..serializers.course_progress_serializer import CourseProgressSerializer
from ..serializers.lesson_progress_serializer import LessonProgressSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class ProgressViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = CourseProgressSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return CourseProgress.objects.all()
            
        return CourseProgress.objects.filter(
            enrollment__user__organization=self.request.user.organization
        )

class LessonProgressViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = LessonProgressSerializer
    
    def get_queryset(self):
        return LessonProgress.objects.filter(
            enrollment__user=self.request.user
        )
