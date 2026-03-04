from rest_framework import serializers
from admin.access.models import Course

class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "description",
            "level",
            "language",
            "thumbnail_url",
            "organization",
            "instructor",
        ]
