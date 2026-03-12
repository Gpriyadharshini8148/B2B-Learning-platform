import os
from rest_framework import serializers
from ..models.image import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image_id', 'image_file', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def validate_image_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError("Only JPG, JPEG, and PNG images are allowed.")
        return value
