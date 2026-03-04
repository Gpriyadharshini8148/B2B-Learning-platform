from django.conf import settings
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from admin.access.models.video import Video
from ..serializers.video_serializer import VideoSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class OrgVideoViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    API for managing video uploads within an organization.
    """
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrgAdminOrReadOnly]
    parser_classes = (MultiPartParser, FormParser) # Necessary for file uploads

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Video.objects.all()
            
        return Video.objects.filter(organization=user.organization)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Video uploaded successfully",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
