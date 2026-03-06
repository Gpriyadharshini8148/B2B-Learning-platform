"""
Syncs passwords from the local Django DB to Keycloak.
Run this once to fix the 'Invalid user credentials' error.

Usage: python fix_keycloak_passwords.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udemy.settings')
django.setup()

from keycloak import KeycloakAdmin
from admin.access.models.user import User

KEYCLOAK_SERVER_URL = os.environ.get('KEYCLOAK_SERVER_URL', 'http://localhost:8080')
KEYCLOAK_REALM = os.environ.get('KEYCLOAK_REALM', 'udemy-clone')

# ---------------------------------------------------------------------------
# Prompt for a temporary password to assign to Keycloak users.
# Instruct them to change it on first login, or you can set per-user below.
# ---------------------------------------------------------------------------
DEFAULT_PASSWORD = input("Enter a default Keycloak password to assign to all users: ").strip()
if not DEFAULT_PASSWORD:
    print("No password entered. Exiting.")
    exit(1)

print(f"\nConnecting to Keycloak at {KEYCLOAK_SERVER_URL} ...")
admin = KeycloakAdmin(
    server_url=KEYCLOAK_SERVER_URL,
    username='admin',
    password='admin',
    user_realm_name='master',
    realm_name=KEYCLOAK_REALM,
    verify=True,
)

users = User.objects.all()
print(f"Found {users.count()} users in local DB.\n")

for user in users:
    email = user.email
    kc_user_id = admin.get_user_id(email)
    if not kc_user_id:
        print(f"  [SKIP] {email} — not found in Keycloak")
        continue

    try:
        admin.set_user_password(user_id=kc_user_id, password=DEFAULT_PASSWORD, temporary=False)
        # Also make sure the user is enabled & verified
        admin.update_user(user_id=kc_user_id, payload={"enabled": True, "emailVerified": True})
        print(f"  [OK]   {email} — password set")
    except Exception as e:
        print(f"  [ERR]  {email} — {e}")

print("\nDone!")
