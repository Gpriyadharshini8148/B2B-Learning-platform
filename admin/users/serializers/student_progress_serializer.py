from rest_framework import serializers
from admin.access.models.course_progress import CourseProgress

class StudentCourseProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)

    class Meta:
        model = CourseProgress
        fields = ('id', 'progress_percentage', 'completed_at', 'course_title')
        read_only_fields = ('completed_at',)
