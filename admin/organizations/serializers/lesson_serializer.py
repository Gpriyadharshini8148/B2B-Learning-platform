from rest_framework import serializers
from admin.access.models.lesson import Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id', 'title', 'order_number', 'is_preview', 'organization', 'section', 'video', 'duration_seconds')
        read_only_fields = ('id', 'organization', 'section')
        extra_kwargs = {
            'video': {'required': True, 'allow_null': False}
        }



