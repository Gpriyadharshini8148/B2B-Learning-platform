from rest_framework import viewsets
from ..models.lesson import Lesson
from ..serializers.lesson_serializer import LessonSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class LessonViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Lesson
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
