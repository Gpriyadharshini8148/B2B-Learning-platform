from rest_framework import viewsets, permissions
from admin.access.models import Quiz, QuizAttempt
from admin.organizations.serializers import QuizSerializer
# We can create a QuizAttemptSerializer here or in users/serializers/
from rest_framework import serializers

class QuizAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAttempt
        fields = ('id', 'quiz', 'score', 'is_passed', 'end_time', 'created_at')
        read_only_fields = ('id', 'user', 'score', 'is_passed', 'end_time', 'created_at')

class StudentQuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Learner-facing Quiz view: View quizzes they have access to via enrollment.
    """
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.none()

    def get_queryset(self):
        user = self.request.user
        # Optionally filter by what they are enrolled in, 
        # but for now we filter by their organization's quizzes
        return Quiz.objects.filter(organization=user.organization)

class StudentQuizAttemptViewSet(viewsets.ModelViewSet):
    """
    Learner-facing Quiz Attempt view: Track their results.
    """
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = QuizAttempt.objects.none()

    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
