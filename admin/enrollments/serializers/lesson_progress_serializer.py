from rest_framework import serializers
from ..models.lesson_progress import LessonProgress

class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = '__all__'
