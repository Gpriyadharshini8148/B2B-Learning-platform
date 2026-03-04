from rest_framework import serializers
from admin.access.models import Lesson, Video


class VideoNestedSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ["id", "title", "url", "duration_seconds"]

    def get_url(self, obj):
        request = self.context.get('request')
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return None


class LessonDetailSerializer(serializers.ModelSerializer):
    video = VideoNestedSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "duration_seconds",
            "order_number",
            "section",
            "video",
            "is_preview",
        ]
