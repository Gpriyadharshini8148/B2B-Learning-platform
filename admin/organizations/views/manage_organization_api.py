from rest_framework import viewsets, permissions, status, serializers, pagination
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from django.core.signing import TimestampSigner
from drf_spectacular.utils import extend_schema
from admin.organizations.serializers.manage_organization_serializer import (
    ManageOrganizationListSerializer, 
    ManageOrganizationCreateSerializer
)
from django.conf import settings
from admin.access.permissions.tenant_permissions import IsSuperAdmin
from admin.organizations.models.organization import Organization
from admin.access.models.user import User as CustomUser
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole
from admin.access.authentication.keycloak_manager import create_organization_group, register_user_with_role, setup_base_roles


class ManageOrganizationsViewSet(viewsets.GenericViewSet):
    """
    Manage Organizations API for Super Admins.
    Allows creating, viewing, updating, activating/deactivating, and deleting Orgs.
    """
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
    queryset = Organization.objects.all().order_by('-created_at')
    serializer_class = ManageOrganizationListSerializer
    pagination_class = pagination.PageNumberPagination

    @extend_schema(responses={200: ManageOrganizationListSerializer(many=True)})
    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        data = []
        source = page if page is not None else queryset
        
        for org in source:
            data.append({
                "id": org.id,
                "name": org.name,
                "subdomain": org.subdomain,
                "status": "active" if org.is_active else "inactive"
            })
            
        if page is not None:
            return self.get_paginated_response(data)
            
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ManageOrganizationCreateSerializer,
        responses={201: dict}
    )
    def create(self, request):
        name = request.data.get("name")
        subdomain = request.data.get("subdomain")
        email = request.data.get("email")
        password = request.data.get("password") or "Admin@123"

        if not all([name, subdomain, email]):
            return Response({"error": "name, subdomain, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if Organization.objects.filter(subdomain__iexact=subdomain).exists():
            return Response({"error": "Organization with this subdomain already exists."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create Organization
        org = Organization.objects.create(
            name=name,
            subdomain=subdomain,
            is_active=True,
            is_verified=True,
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
            password_hash=make_password(password),
            is_active=True,
            is_verified=True,
            approval_status='approved'
        )

        UserRole.objects.create(user=admin_user, role=admin_role)

        # --- Hierarchical Keycloak Integration ---
        # 1. Ensure base roles exist
        setup_base_roles()

        # 2. Create the Organization Group
        group_success, group_msg = create_organization_group(subdomain)
        
        # 3. Register User and set password
        kc_user_success, kc_user_msg = register_user_with_role(
            email=email, 
            password=password,
            role_name="organization_admin",
            organization_subdomain=subdomain,
            enabled=True
        )

        keycloak_msg = ""
        if group_success and kc_user_success:
            keycloak_msg = " Keycloak group and admin user successfully provisioned."
        else:
            keycloak_msg = f" Note: Keycloak provisioning hit issues: {group_msg if not group_success else kc_user_msg}"

        return Response({
            "message": f"Organization {org.name} created.{keycloak_msg} Admin user is: {email}.",
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

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Manually reset the password for the Organization Admin.
        """
        try:
            org = Organization.objects.get(pk=pk)
            new_password = request.data.get("password")
            
            if not new_password:
                return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Find the primary admin
            admin_user = CustomUser.objects.filter(
                organization=org, 
                userrole__role__name__in=['organization_admin', 'admin', 'org_admin']
            ).first()

            if not admin_user:
                return Response({"error": "No admin user found for this organization."}, status=status.HTTP_404_NOT_FOUND)

            admin_user.password_hash = make_password(new_password)
            admin_user.save()

            return Response({"message": f"Password for {admin_user.email} has been updated successfully."})
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

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
            pending_admins = CustomUser.objects.filter(organization=org, approval_status='pending')
            
            for admin in pending_admins:
                admin.is_active = True
                admin.is_verified = True
                admin.approval_status = 'approved'
                admin.save()
                
                # Register the approved Admin in Keycloak
                register_user_with_role(
                    email=admin.email,
                    role_name="organization_admin",
                    organization_subdomain=org.subdomain
                )
            
            return Response({"message": "Organization and its admin approved successfully in DB and Keycloak."}, status=status.HTTP_200_OK)
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
