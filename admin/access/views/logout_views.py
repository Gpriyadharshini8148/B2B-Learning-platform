from rest_framework import views, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from admin.access.authentication.serializers import LogoutSerializer

class LogoutView(views.APIView):
    """
    Logs out the user by setting is_logged_in to False.
    Requires an authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=LogoutSerializer, responses={200: {"type": "object", "properties": {"message": {"type": "string"}}}})
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user:
                user.is_logged_in = False
                user.save()
                return Response({"message": "Logout Successful."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
