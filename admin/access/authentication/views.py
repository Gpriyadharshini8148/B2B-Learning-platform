from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import KeycloakLoginSerializer

class KeycloakTokenObtainPairView(APIView):
    """
    View to authenticate users via Keycloak.
    This replaces the standard SimpleJWT login to ensure all authentication
    goes through Keycloak.
    """
    authentication_classes = [] # Don't try to authenticate the login request
    permission_classes = [permissions.AllowAny]
    serializer_class = KeycloakLoginSerializer

    @extend_schema(
        request=KeycloakLoginSerializer,
        responses={200: KeycloakLoginSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
