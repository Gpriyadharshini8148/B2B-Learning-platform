from rest_framework import serializers
from admin.access.models.course_assignment import CourseAssignment

class CourseAssignmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = CourseAssignment
        fields = ['id', 'course', 'user', 'course_name', 'user_email', 'due_date', 'created_at', 'assigned_by']
        read_only_fields = ['assigned_by', 'created_at']
