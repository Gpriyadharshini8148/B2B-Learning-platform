import os
from keycloak import KeycloakOpenID
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from admin.access.models.user import User
from django.conf import settings
from admin.access.models import Role, UserRole
from admin.organizations.models.organization import Organization

# Keycloak Configuration from
#  Environment Variables or Settings
KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL', 'http://127.0.0.1:8080/')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'udemy-clone')  
KEYCLOAK_CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'django-backend')
KEYCLOAK_CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET', None)

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET
)

class KeycloakAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]

        try:
            # Verify Token with Keycloak
            user_info = keycloak_openid.userinfo(token)
            
            # Extract user details from Keycloak info
            email = user_info.get('email')
            if not email:
                raise AuthenticationFailed('Token provided does not contain email information.')

            # Get or create user in local database
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': user_info.get('given_name', user_info.get('name', '').split(' ')[0]),
                    'last_name': user_info.get('family_name', user_info.get('name', '').split(' ')[-1] if ' ' in user_info.get('name', '') else ''),
                    'is_active': True,
                    'is_verified': True,
                    'approval_status': 'approved'
                }
            )

            # Synchronize Roles and Organization from Keycloak

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

            # Target role synchronization (Role from Keycloak Realm Roles)
            keycloak_roles = user_info.get('realm_access', {}).get('roles', [])
            target_role_names = [choice[0] for choice in Role.ROLE_CHOICES]
            needs_save = False
            for role_name in target_role_names:
                if role_name in keycloak_roles:
                    # If super_admin, set Django flags
                    if role_name == 'super_admin':
                        if not user.is_superuser or not user.is_staff:
                            user.is_superuser = True
                            user.is_staff = True
                            needs_save = True

                    role_obj, _ = Role.objects.get_or_create(
                        name=role_name,
                        organization=user.organization,
                        defaults={'description': f'System role: {role_name}'}
                    )
                    UserRole.objects.get_or_create(user=user, role=role_obj)

            # Check and sync is_logged_in state so valid tokens are allowed
            if not user.is_logged_in:
                user.is_logged_in = True
                needs_save = True

            if needs_save:
                user.save()

            if not user.is_active:
                raise AuthenticationFailed('User account is inactive.')

            return (user, token)

        except AuthenticationFailed:
            # Re-raise our own AuthenticationFailed
            raise
        except Exception as e:
            # If a token was provided but Keycloak failed to verify it, raise AuthenticationFailed
            error_msg = str(e)
            if '401' in error_msg or 'Unauthorized' in error_msg:
                raise AuthenticationFailed('Invalid or expired token.')
            raise AuthenticationFailed(f'Keycloak Auth Error: {error_msg}')

def authenticate_with_keycloak(username, password):
    """
    Helper function to authenticate a user directly with Keycloak 
    using the resource owner password credentials grant.
    """
    return keycloak_openid.token(username, password)
