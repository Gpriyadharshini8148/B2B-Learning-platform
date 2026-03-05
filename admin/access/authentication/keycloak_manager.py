import logging
from keycloak import KeycloakAdmin
import os

logger = logging.getLogger(__name__)

def get_keycloak_admin():
    """
    Returns an authenticated KeycloakAdmin client for the target realm.
    We use the Master realm admin credentials to manage the 'udemy-clone' realm.
    """
    return KeycloakAdmin(
        server_url=os.environ.get('KEYCLOAK_SERVER_URL', 'http://127.0.0.1:8080/'),
        username=os.environ.get('KEYCLOAK_ADMIN', 'admin'),
        password=os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin'),
        user_realm_name="master", # We are logging in using the master realm's admin credentials
        realm_name=os.environ.get('KEYCLOAK_REALM', 'udemy-clone'), # We are administrating the udemy-clone realm
        verify=True
    )

def create_organization_group(subdomain):
    """
    Creates a Group in the 'udemy-clone' realm for a specific organization.
    """
    try:
        keycloak_admin = get_keycloak_admin()
        group_name = f"Org:{subdomain}"
        groups = keycloak_admin.get_groups()
        if not any(g['name'] == group_name for g in groups):
            keycloak_admin.create_group(payload={"name": group_name})
        logger.info(f"Keycloak Group '{group_name}' created.")
        return True, group_name
    except Exception as e:
        logger.error(f"Error creating Keycloak group: {str(e)}")
        return False, str(e)

def setup_base_roles():
    """
    Ensures the standard roles exist in the 'udemy-clone' realm.
    """
    try:
        keycloak_admin = get_keycloak_admin()
        target_roles = ['super_admin', 'organization_admin', 'organization_user']
        existing_roles = [r['name'] for r in keycloak_admin.get_realm_roles()]
        for role_name in target_roles:
            if role_name not in existing_roles:
                keycloak_admin.create_realm_role(payload={"name": role_name})
        return True, "Roles ensured."
    except Exception as e:
        logger.error(f"Error setting up roles: {str(e)}")
        return False, str(e)

def register_user_with_role(email, role_name, organization_subdomain=None, password=None, enabled=True):
    """
    Creates or updates a user in Keycloak with a specific role and organization group.
    """
    try:
        keycloak_admin = get_keycloak_admin()

        # 1. Create user if not exists
        try:
            keycloak_admin.create_user(payload={
                "email": email,
                "username": email,
                "enabled": enabled,
                "emailVerified": enabled,
            })
        except Exception:
            # User likely already exists – that's fine
            pass

        user_id = keycloak_admin.get_user_id(email)
        if not user_id:
            raise ValueError(f"Could not find or create Keycloak user for email: {email}")

        # 2. Set password if provided
        if password:
            keycloak_admin.set_user_password(user_id=user_id, password=password, temporary=False)
        
        # If re-enabling an existing user, also update their enabled status
        if enabled:
            keycloak_admin.update_user(user_id=user_id, payload={"enabled": True, "emailVerified": True})

        # 3. Assign realm role
        role = keycloak_admin.get_realm_role(role_name)
        keycloak_admin.assign_realm_roles(user_id, roles=[role])

        # 4. Assign org group if provided
        if organization_subdomain:
            group_name = f"Org:{organization_subdomain}"
            groups = keycloak_admin.get_groups()
            group = next((g for g in groups if g['name'] == group_name), None)
            if group:
                keycloak_admin.group_user_add(user_id, group['id'])

        return True, "User registered in Keycloak."
    except Exception as e:
        logger.error(f"Keycloak User Registration failed: {str(e)}")
        return False, str(e)

def enable_keycloak_user(email):
    """
    Activates a previously created but disabled Keycloak user.
    """
    try:
        keycloak_admin = get_keycloak_admin()
        user_id = keycloak_admin.get_user_id(email)
        if user_id:
            keycloak_admin.update_user(user_id=user_id, payload={"enabled": True, "emailVerified": True})
            return True, "User activated."
        return False, "User not found in Keycloak."
    except Exception as e:
        logger.error(f"Failed to enable Keycloak user: {str(e)}")
        return False, str(e)
