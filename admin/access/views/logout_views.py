from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from admin.access.authentication.serializers import LogoutSerializer
from admin.access.authentication.keycloak_auth import keycloak_openid
import logging

class LogoutView(views.APIView):
    """
    Logs out the user by clearing the is_logged_in flag and
    invalidating the refresh token in Keycloak.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={200: dict})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data.get('refresh_token')
            
            # --- 1. Keycloak Logout ---
            try:
                keycloak_openid.logout(refresh_token)
            except Exception as e:
                # If keycloak logout fails, we still want to clear the local session
                # but we'll log it.
                logger = logging.getLogger(__name__)
                logger.error(f"Keycloak logout failed: {str(e)}")

            # --- 2. Django Session Cleanup ---
            user = request.user
            if user:
                user.is_logged_in = False
                user.save()
            
            return Response({"message": "Logout Successful."}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
