from rest_framework import serializers
from admin.access.models import Quiz, Question, Option

class OptionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]

class QuestionNestedSerializer(serializers.ModelSerializer):
    options = OptionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "quiz", "question_type", "marks", "options"]

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "passing_score", "course", "lesson", "questions"]
