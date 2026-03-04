
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udemy.settings')
django.setup()

from admin.access.models.user import User as CustomUser
from admin.organizations.models.organization import Organization

def check_valid_data():
    print("--- Organizations ---")
    orgs = Organization.objects.all()
    for o in orgs:
        print(f"Name: {o.name}, Subdomain: {o.subdomain}")

    print("\n--- Users in 'mailinatoredu' ---")
    users = CustomUser.objects.filter(organization__subdomain='mailinatoredu')
    if not users.exists():
        # Let's see any users at all
        print("No users in mailinatoredu. All users:")
        all_users = CustomUser.objects.all()[:5]
        for u in all_users:
            print(f"Email: {u.email}, Org: {u.organization.subdomain if u.organization else 'None'}")
    else:
        for u in users:
            print(f"Email: {u.email}")

if __name__ == "__main__":
    check_valid_data()
