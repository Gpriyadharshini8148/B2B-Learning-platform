from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from admin.access.models.user import User

class ResetPasswordView(views.APIView):
    """
    API for users to set or reset their password using a signed token.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request={'token': str, 'password': str})
    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')

        if not token or not password:
            return Response({"error": "token and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        signer = TimestampSigner()
        try:
            # Token is valid for 24 hours (86400 seconds)
            email = signer.unsign(token, max_age=86400)
        except SignatureExpired:
            return Response({"error": "Password reset link has expired."}, status=status.HTTP_400_BAD_REQUEST)
        except BadSignature:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Set the new password
        user.password_hash = make_password(password)
        user.save()

        return Response({"message": "Password successfully set/reset. You can now login."}, status=status.HTTP_200_OK)
