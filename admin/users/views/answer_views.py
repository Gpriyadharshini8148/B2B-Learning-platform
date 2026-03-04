from rest_framework import viewsets, permissions
from admin.access.models import Answer
from admin.users.serializers.answer_serializer import AnswerSerializer

class UserAnswerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def perform_create(self, serializer):
        org = getattr(self.request.user, "organization", None)
        serializer.save(organization=org)
