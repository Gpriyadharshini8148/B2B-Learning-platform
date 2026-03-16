from rest_framework import permissions
from django.conf import settings

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to super admins.
    """
    def has_permission(self, request, view):
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        return bool(request.user and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email))

class IsOrganizationMember(permissions.BasePermission):
    """
    Allows access to any authenticated user.
    Organization membership is checked at the data level (queryset).
    """
    def has_permission(self, request, view):
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        # Super Admin bypass
        if request.user and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email):
            return True
            
        return bool(request.user and request.user.is_authenticated)

class IsOrganizationAdmin(permissions.BasePermission):
    """
    Allows access to Organization Admins for their own organization data.
    """
    def has_permission(self, request, view):
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        # Super Admin / Staff bypass
        if request.user and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email or request.user.is_staff):
            return True
        
        # Check if user is an admin for their organization
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'is_org_admin', False))

    def has_object_permission(self, request, view, obj):
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        if request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email:
            return True
        
        # Check ownership at organization level
        if hasattr(obj, 'organization'):
            return obj.organization_id == request.user.organization_id
        
        if hasattr(obj, 'user'):
             return obj.user.organization_id == request.user.organization_id

        if hasattr(request.user, 'organization') and isinstance(obj, type(request.user.organization)):
            return obj.id == request.user.organization_id

        return False

class IsOrgAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only organization admins to edit, but allow anyone to view (if authenticated).
    """
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False

        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        # 1. Super Admin / Staff Bypass
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email or user.is_staff:
            return True

        # 2. Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # 3. Writing permissions only for Organization Admins
        # Must have is_org_admin property True AND belong to an organization
        is_admin = getattr(user, 'is_org_admin', False)
        has_org = hasattr(user, 'organization_id') and user.organization_id is not None
        
        return bool(is_admin and has_org)

class TenantSafeViewSetMixin:
    """
    Mixin to automatically filter querysets based on the user's organization.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Bypass for drf-spectacular schema generation
        if getattr(self, 'swagger_fake_view', False):
            return queryset.none()
            
        user = self.request.user

        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')

        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return queryset
        
        # Mixin for queryset filtering
        # Specialized filtering for Enrollment (which doesn't have its own direct 'organization' field)
        if queryset.model.__name__ == 'Enrollment':
            # Learners see their OWN enrollments
            # Admins see their ORG's enrollments
            if getattr(user, 'is_org_admin', False):
                return queryset.filter(user__organization=user.organization)
            return queryset.filter(user=user)

        # Filter by organization if the model has a direct link to it
        if hasattr(queryset.model, 'organization'):
            return queryset.filter(organization=user.organization)
        
        # For the User model
        if queryset.model.__name__ == 'User':
            return queryset.filter(organization=user.organization)

        return queryset
