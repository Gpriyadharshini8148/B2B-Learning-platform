from rest_framework import viewsets, permissions
from ..models.image import Image
from ..serializers.image_serializer import ImageSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class ImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for uploading and managing images.
    """
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Optional: restrict images to those uploaded by the user or organization
        return super().get_queryset()
