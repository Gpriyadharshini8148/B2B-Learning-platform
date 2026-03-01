from rest_framework import viewsets
from ..models.lesson import Lesson
from ..serializers.lesson_serializer import LessonSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class LessonViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Lesson.objects.all()
            
        return Lesson.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )
