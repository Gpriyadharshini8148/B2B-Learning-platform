from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema
from admin.access.authentication.refresh_serializers import RefreshTokenSerializer

class KeycloakTokenRefreshView(APIView):
    """
    Takes a refresh token and returns an access token if the refresh token is valid.
    Uses Keycloak's token endpoint under the hood.
    """
    authentication_classes = [] # Don't try to authenticate the refresh request
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=RefreshTokenSerializer,
        responses={200: RefreshTokenSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
