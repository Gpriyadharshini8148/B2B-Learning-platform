from rest_framework import serializers
from admin.access.models import Question, Option

class OptionNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]

class QuestionDetailSerializer(serializers.ModelSerializer):
    options = OptionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "quiz", "question_type", "marks", "options"]
