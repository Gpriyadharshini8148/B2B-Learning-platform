from rest_framework import serializers
from admin.access.models.lesson_progress import LessonProgress

class LessonProgressSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='enrollment.user.email', read_only=True)
    course_title = serializers.CharField(source='enrollment.course.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonProgress
        fields = ('id', 'is_completed', 'watch_time_seconds', 'enrollment', 'user_email', 'course_title', 'lesson', 'lesson_title')
        read_only_fields = ('watch_time_seconds',)
