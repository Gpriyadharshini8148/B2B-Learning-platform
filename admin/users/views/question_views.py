from rest_framework import viewsets, permissions
from admin.access.models import Question
from admin.users.serializers.question_serializer import QuestionDetailSerializer

class UserQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner‑side Read-Only view for Question."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionDetailSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Question.objects.filter(organization=org)
