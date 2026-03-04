from rest_framework import serializers
from admin.access.models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'passing_score')
        read_only_fields = ('id', 'organization', 'course', 'lesson')
