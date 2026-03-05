from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from admin.access.models.user import User
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole
from admin.access.authentication.keycloak_manager import register_user_with_role, setup_base_roles


class Command(BaseCommand):
    help = 'Creates or updates the Super Admin user in both Django and Keycloak'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='gpriyadharshini9965@gmail.com')
        parser.add_argument('--password', type=str, default='Gpriya@123')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']

        self.stdout.write(f'Setting up Super Admin: {email}')

        # 1. Create or update the Django user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': 'Super',
                'last_name': 'Admin',
                'password_hash': make_password(password),
                'is_active': True,
                'is_superuser': True,
                'is_staff': True,
                'approval_status': 'approved',
                'is_verified': True,
            }
        )

        if not created:
            user.is_superuser = True
            user.is_staff = True
            user.is_active = True
            user.is_verified = True
            user.approval_status = 'approved'
            user.save()
            self.stdout.write('  → Existing user updated to Super Admin')
        else:
            self.stdout.write('  → New Super Admin user created')

        # 2. Assign super_admin role in Django DB
        role, _ = Role.objects.get_or_create(
            name='super_admin',
            organization=None,
            defaults={'description': 'Platform Super Administrator'}
        )
        UserRole.objects.get_or_create(user=user, role=role)
        self.stdout.write('  → Django role assigned')

        # 3. Register in Keycloak
        setup_base_roles()
        success, msg = register_user_with_role(
            email=email,
            role_name='super_admin',
            password=password,
            enabled=True
        )
        if success:
            self.stdout.write(self.style.SUCCESS(f'  → Keycloak: {msg}'))
        else:
            self.stdout.write(self.style.WARNING(f'  → Keycloak warning: {msg}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuper Admin ready!'))
        self.stdout.write(f'  Email:    {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Login at: POST http://localhost:8000/api/access/auth/keycloak/login/')
