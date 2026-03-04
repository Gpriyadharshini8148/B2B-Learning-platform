from rest_framework import serializers
from admin.access.models import Section, Lesson

class LessonNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "order_number", "is_preview"]

class SectionDetailSerializer(serializers.ModelSerializer):
    lessons = LessonNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "title", "order_number", "course", "lessons"]
