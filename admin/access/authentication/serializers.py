from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from admin.access.models.user import User
from django.contrib.auth.hashers import check_password
from django.core.validators import validate_email as django_validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
import re
from admin.access.models import Role, UserRole
from admin.organizations.models.organization import Organization
from django.conf import settings
from .keycloak_auth import keycloak_openid, authenticate_with_keycloak

def validate_password_strength(value):
    if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', value):
        raise serializers.ValidationError(
            "Password must be at least 8 characters long and contain at least one lowercase letter, one uppercase letter, one digit, and one special character."
        )
    return value

class KeycloakLoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate with Keycloak
        try:
            token_data = authenticate_with_keycloak(email, password)
        except Exception as e:
            raise serializers.ValidationError({"detail": f"Keycloak authentication failed: {str(e)}"})
        
        if not token_data:
            raise serializers.ValidationError({"detail": "Invalid credentials or Keycloak authentication failed."})

        # 2. Synchronize user with local DB and handle "already logged in" check
        try:
            from .keycloak_auth import keycloak_openid
            user_info = keycloak_openid.userinfo(token_data['access_token'])
            
            user = User.objects.filter(email=email).first()
            
            if user:
                # Check for existing session
                if user.is_logged_in:
                    # Check if the user is a super admin
                    # (Either via Django flag or Keycloak role info)
                    keycloak_roles = user_info.get('realm_access', {}).get('roles', [])
                    is_super = user.is_superuser or 'super_admin' in keycloak_roles
                    
                    if not is_super:
                        raise serializers.ValidationError({"detail": "User is already logged in. Please log out first."})
            
            if not user:
                user = User.objects.create(
                    email=email,
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    is_active=True,
                    is_verified=True,
                    approval_status='approved'
                )
            
            # Update/Set logged in flag
            user.is_logged_in = True
            user.save()



            # Sync Organization (from Keycloak Groups)
            groups = user_info.get('groups', [])
            for group in groups:
                if group.startswith('Org:'):
                    subdomain = group.split(':')[1]
                    try:
                        org = Organization.objects.get(subdomain=subdomain)
                        user.organization = org
                        user.save()
                        break
                    except Organization.DoesNotExist:
                        pass

            # Sync Roles (from Keycloak Realm Roles)
            keycloak_roles = user_info.get('realm_access', {}).get('roles', [])
            target_role_names = [choice[0] for choice in Role.ROLE_CHOICES]
            for role_name in target_role_names:
                if role_name in keycloak_roles:
                    # If super_admin, set Django flags
                    if role_name == 'super_admin':
                        user.is_superuser = True
                        user.is_staff = True
                        user.save()
                    
                    role_obj, _ = Role.objects.get_or_create(
                        name=role_name,
                        organization=user.organization
                    )
                    UserRole.objects.get_or_create(user=user, role=role_obj)
        except serializers.ValidationError:
            raise
        except Exception as e:
            raise serializers.ValidationError({"detail": f"User synchronization failed: {str(e)}"})

        return {
            "message": "logged in successfully via Keycloak",
            "access_token": token_data.get('access_token'),
            "refresh_token": token_data.get('refresh_token'),
            "expires_in": token_data.get('expires_in'),
            "token_type": token_data.get('token_type'),
        }

class UnifiedLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()
    access_token = serializers.CharField(required=False)

class OrganizationSignupSerializer(serializers.Serializer):
    admin_email = serializers.EmailField()
    password = serializers.CharField(validators=[validate_password_strength], required=False)
    name = serializers.CharField()
    subdomain = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('admin_email')
        if not email:
            raise serializers.ValidationError({"admin_email": "Admin email is required."})
        
        try:
            django_validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError({"admin_email": "Enter a valid email address."})
            
        return attrs

class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(validators=[validate_password_strength])
    organization_subdomain = serializers.CharField(required=False)

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
