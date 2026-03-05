from rest_framework import serializers
from admin.access.models.enrollment import Enrollment

class StudentEnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    instructor_name = serializers.CharField(source='course.instructor.email', read_only=True) # instructor.email for now as name might be missing
    thumbnail = serializers.URLField(source='course.thumbnail_url', read_only=True)
    progress = serializers.SerializerMethodField()
    rating = serializers.FloatField(default=0.0, read_only=True) # Rating system to be implemented later

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'instructor_name', 'thumbnail', 'progress', 'rating', 'status']

    def get_progress(self, obj) -> float:
        if hasattr(obj, 'progress'):
            return obj.progress.progress_percentage
        return 0.0
