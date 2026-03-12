from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core import signing
from drf_spectacular.utils import extend_schema
from ..models.certificate import Certificate

class VerifyCertificateView(views.APIView):
    """
    Public API to verify a cryptographically signed certificate link.
    This ensures certificates cannot be guessed or modified.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses={200: dict, 403: dict})
    def get(self, request):
        token = request.query_params.get('token')
        if not token:
             return Response({"error": "Certificate token is missing."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Cryptographically verify and decyrpt the token
            data = signing.loads(token)
            enrollment_id = data.get('enrollment_id')
            
            # Fetch the actual certificate to make sure it exists
            cert = Certificate.objects.get(enrollment_id=enrollment_id)
            
            # Return human-readable certificate data
            return Response({
                "status": "Verified",
                "message": f"This is a valid certificate for Student: {cert.enrollment.user.email}",
                "course": f"Course: {cert.enrollment.course.title}",
                "issued_on": cert.created_at.strftime('%Y-%m-%d'),
                "details": {
                    "enrollment_id": enrollment_id,
                    "student": cert.enrollment.user.email,
                    "digital_signature": token[-10:] # Show only the signature part
                }
            }, status=status.HTTP_200_OK)
            
        except (signing.BadSignature, Certificate.DoesNotExist):
            return Response({"error": "This is NOT a valid certificate or the link has been tampered with."}, 
                            status=status.HTTP_403_FORBIDDEN)
