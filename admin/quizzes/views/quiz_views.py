from rest_framework import viewsets
from ..models.quiz import Quiz
from ..serializers.quiz_serializer import QuizSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class QuizViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Quiz
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
