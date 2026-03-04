from rest_framework import serializers
from admin.access.models.course import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = (
            'id', 'organization', 'created_at', 'updated_at', 
            'is_active', 'is_deleted', 'created_by', 'updated_by', 
            'deleted_by', 'deleted_at'
        )


