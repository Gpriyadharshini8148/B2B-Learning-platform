from rest_framework import serializers
from admin.access.models.video import Video

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ('id', 'title', 'video_file', 'duration_seconds', 'organization')

