from rest_framework import serializers
from ..models.course_progress import CourseProgress

class CourseProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgress
        fields = '__all__'
