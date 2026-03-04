from rest_framework import serializers
from admin.access.models import Answer

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct", "question"]
        read_only_fields = ["id"]
