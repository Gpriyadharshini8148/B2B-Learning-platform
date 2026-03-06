from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from admin.access.models.certificate import Certificate
from admin.organizations.serializers.certificate_serializer import CertificateSerializer

@extend_schema(tags=['User Certificates'])
class StudentCertificateViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API for users (students) to view their own earned certificates.
    Allows listing all earned certificates and retrieving specific ones.
    """
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()
            
        user = self.request.user
        # A user can only see certificates for courses they have completed
        return Certificate.objects.filter(
            enrollment__user=user,
            enrollment__status='completed'
        ).select_related('enrollment__course', 'enrollment__user')
