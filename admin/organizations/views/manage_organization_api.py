from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from admin.access.permissions.tenant_permissions import IsSuperAdmin
from admin.organizations.models.organization import Organization
from admin.access.models.user import User as CustomUser
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole

class ManageOrganizationsViewSet(viewsets.ViewSet):
    """
    Manage Organizations API for Super Admins.
    Allows creating, viewing, updating, activating/deactivating, and deleting Orgs.
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    @extend_schema(responses={200: list})
    def list(self, request):
        orgs = Organization.objects.all().order_by('-created_at')
        data = []
        for org in orgs:
            data.append({
                "id": org.id,
                "name": org.name,
                "subdomain": org.subdomain,
                "status": "active" if org.is_active else "inactive"
            })
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(request=dict, responses={201: dict})
    def create(self, request):
        name = request.data.get("name")
        subdomain = request.data.get("subdomain")
        email = request.data.get("email")

        if not all([name, subdomain, email]):
            return Response({"error": "name, subdomain, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if Organization.objects.filter(subdomain=subdomain).exists():
            return Response({"error": "Organization with this subdomain already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Organization
        org = Organization.objects.create(
            name=name,
            subdomain=subdomain,
            is_active=True, # Active by default when created by Super Admin
            approval_status='approved'
        )

        # Create Org Admin Role if it doesn't exist
        admin_role, _ = Role.objects.get_or_create(
            name="organization_admin",
            organization=org,
            defaults={"description": "Organization Administrator"}
        )

        # Create Admin User
        admin_user = CustomUser.objects.create(
            email=email,
            first_name="Admin",
            last_name=name,
            organization=org,
            password_hash=make_password("Admin@123"), # Default password, easily reset
            is_active=True,
            approval_status='approved'
        )

        UserRole.objects.create(user=admin_user, role=admin_role)

        return Response({
            "id": org.id,
            "name": org.name,
            "subdomain": org.subdomain,
            "email": email,
            "status": "active"
        }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        # Find admins
        org_admins = CustomUser.objects.filter(
            organization=org, 
            userrole__role__name__in=['organization_admin', 'admin', 'org_admin']
        ).distinct()

        # Users total
        total_users = CustomUser.objects.filter(organization=org).count()

        data = {
            "id": org.id,
            "name": org.name,
            "subdomain": org.subdomain,
            "email": org_admins.first().email if org_admins.exists() else None,
            "status": "active" if org.is_active else "inactive",
            "admins_count": org_admins.count(),
            "users_count": total_users,
            "admins": [{"id": a.id, "email": a.email, "name": f"{a.first_name} {a.last_name}".strip()} for a in org_admins],
        }
        return Response(data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if "name" in request.data:
            org.name = request.data["name"]
        if "subdomain" in request.data:
            org.subdomain = request.data["subdomain"]
        org.save()

        return Response({"message": "Organization updated successfully.", "id": org.id, "name": org.name})

    def partial_update(self, request, pk=None):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if "is_active" in request.data:
            # Activate or Deactivate Organization
            is_active = request.data.get("is_active")
            org.is_active = bool(is_active)
            org.save()

            # Optional: Deactivate all its users so they cannot login when org is inactive
            if org.is_active == False:
                 CustomUser.objects.filter(organization=org).update(is_active=False)
            
            status_text = "active" if org.is_active else "inactive"
            return Response({"message": f"Organization disabled functionality activated. Status is now {status_text}."})

        return Response({"error": "Please provide is_active field to patch."}, status=status.HTTP_400_BAD_REQUEST)

    from rest_framework.decorators import action
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        try:
            org = Organization.objects.get(pk=pk)
            
            if org.approval_status != 'pending':
                return Response({"message": f"Organization is already {org.approval_status}"}, status=status.HTTP_400_BAD_REQUEST)

            org.approval_status = 'approved'
            org.is_active = True
            org.is_verified = True
            org.save()
            
            # Activate the pending admins inside this organization
            CustomUser.objects.filter(organization=org, approval_status='pending').update(
                is_active=True, 
                is_verified=True,
                approval_status='approved'
            )
            
            return Response({"message": "Organization and its admin approved successfully. Admin can now login."}, status=status.HTTP_200_OK)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        try:
            org = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        org_name = org.name
        org.delete()  # Cascade will remove users and roles attached to this org.
        return Response({"message": f"Organization '{org_name}' deleted successfully."}, status=status.HTTP_200_OK)
