from rest_framework import serializers
from admin.access.models.course import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            'id', 'organization', 'instructor', 'category', 'title', 
            'description', 'level', 'language', 'thumbnail_url', 
            'is_global', 'is_published', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'organization', 'created_at', 'updated_at'
        )


