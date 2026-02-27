from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema
from rest_framework import permissions
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Extends generic TokenObtainPairView to include custom 
    organization and user details in the JWT token payload.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=CustomTokenObtainPairSerializer,
        responses={200: CustomTokenObtainPairSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
