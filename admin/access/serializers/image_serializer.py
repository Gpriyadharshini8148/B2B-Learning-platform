from rest_framework import serializers
from ..models.image import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_id', 'image_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']
