from rest_framework import views, permissions, status
from rest_framework.response import Response
from admin.access.serializers.user_serializer import UserSerializer

class UserProfileAPIView(views.APIView):
    """
    GET /api/user/profile
    Load user profile, identify logged-in user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
