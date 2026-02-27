from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from admin.access.models.user import User
from django.contrib.auth.hashers import check_password
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from django.conf import settings
def validate_password_strength(value):
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
        raise serializers.ValidationError(
            "Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    return value

class CustomTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)

        # Add custom claims from the User model
        token['email'] = getattr(user, 'email', '')
        token['first_name'] = getattr(user, 'first_name', '')
        token['last_name'] = getattr(user, 'last_name', '')
        
        if getattr(user, 'organization_id', None):
            token['organization_id'] = user.organization.id
            token['organization_name'] = user.organization.name

        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "No active account found with the given email."})

        if getattr(user, 'approval_status', '') == 'pending':
            raise serializers.ValidationError({"detail": "Your account is still pending approval from the administrator."})
            
        if getattr(user, 'approval_status', '') == 'rejected':
            raise serializers.ValidationError({"detail": "Your account request was rejected."})

        if not user.is_active:
            raise serializers.ValidationError({"detail": "This account is inactive."})

        if not check_password(password, user.password_hash):
            raise serializers.ValidationError({"detail": "Incorrect password."})

        self.user = user

        if user.is_logged_in:
            if user.email != getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com'):
                from rest_framework.exceptions import ValidationError
                raise ValidationError({"error": "User already logged in"})

        user.is_logged_in = True
        user.save()

        # Rename keys and add message
        refresh = self.get_token(user)
        response_data = {
            "message": "logged in success fully",
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh)
        }
        
        return response_data

class UnifiedLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

class OrganizationSignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(validators=[validate_password_strength])
    organization_name = serializers.CharField()
    subdomain = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('username') or attrs.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
        
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError({"email": "Enter a valid email address."})
            
        return attrs

class LearnerSignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(validators=[validate_password_strength])
    organization_subdomain = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('username') or attrs.get('email')
        if not email:
            raise serializers.ValidationError({"email": "Email is required."})
            
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError({"email": "Enter a valid email address."})
            
        return attrs

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
