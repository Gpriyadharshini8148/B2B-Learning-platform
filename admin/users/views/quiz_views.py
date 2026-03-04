from rest_framework import viewsets, permissions
from admin.access.models import Quiz
from admin.users.serializers.quiz_serializer import QuizDetailSerializer

class UserQuizViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner‑side Read-Only view for Quiz."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuizDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Quiz.objects.filter(organization=org)
