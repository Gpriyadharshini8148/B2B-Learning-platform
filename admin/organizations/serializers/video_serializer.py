import os
from rest_framework import serializers
from admin.access.models.video import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'video_file', 'duration_seconds', 'organization')

    def validate_video_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext != '.mp4':
            raise serializers.ValidationError("Only MP4 videos are allowed.")
        return value

