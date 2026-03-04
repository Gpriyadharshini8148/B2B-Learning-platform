from rest_framework import serializers
from admin.access.models import Question

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'text', 'question_type', 'marks', 'quiz')
        read_only_fields = ('id', 'organization', 'quiz')
