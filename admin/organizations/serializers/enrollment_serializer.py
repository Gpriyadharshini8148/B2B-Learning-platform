from rest_framework import serializers
from admin.access.models.enrollment import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Enrollment
        fields = ('id', 'status', 'user', 'user_email', 'course', 'course_title', 'created_at')
        read_only_fields = ('created_at',)
