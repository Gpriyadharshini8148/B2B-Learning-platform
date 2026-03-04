from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework.authentication import SessionAuthentication
from admin.access.models.user import User

from rest_framework_simplejwt.settings import api_settings

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        Overrides the default to return the custom User model instead of the Django default.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification', code='token_not_valid')

        try:
            # SimpleJWT defaults to 'id' for the field.
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found', code='user_not_found')

        if not user.is_active:
            raise AuthenticationFailed('User is inactive', code='user_inactive')

        return user

class CustomSessionAuthentication(SessionAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result:
            user, auth = result
            try:
                # Attempt to find the custom User model instance by email.
                # This allows session-authenticated users to be treated as our custom User model.
                custom_user = User.objects.get(email=user.email)
                return (custom_user, auth)
            except User.DoesNotExist:
                # Fallback to the original user if no custom profile exists.
                pass
        return result
