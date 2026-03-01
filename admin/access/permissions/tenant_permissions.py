from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to super admins.
    """
    def has_permission(self, request, view):
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        return bool(request.user and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email))

class IsOrganizationAdmin(permissions.BasePermission):
    """
    Allows access to Organization Admins for their own organization data.
    """
    def has_permission(self, request, view):
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        # Allow superusers and staff members to bypass the organization check
        if request.user and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email or request.user.is_staff):
            return True
        # For regular org admins, we check for organization_id
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'organization_id') and request.user.organization_id)

    def has_object_permission(self, request, view, obj):
        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        # If the user is a super admin, they have full access
        if request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email:
            return True
        
        # Check if the object belongs to the user's organization
        # This assumes the object has an 'organization' field or is the organization itself.
        if hasattr(obj, 'organization'):
            return obj.organization_id == request.user.organization_id
        
        if hasattr(obj, 'user'): # For models linked to users
             return obj.user.organization_id == request.user.organization_id

        if isinstance(obj, type(request.user.organization)):
            return obj.id == request.user.organization_id

        return False

class TenantSafeViewSetMixin:
    """
    Mixin to automatically filter querysets based on the user's organization.
    Superusers see everything.
    Org Admins see only their organization's data.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        from django.conf import settings
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return queryset
        
        # If the model has an 'organization' field, filter by it
        if hasattr(self.model, 'organization'):
            return queryset.filter(organization=user.organization)
        
        # For the User model itself
        if self.model.__name__ == 'User':
            return queryset.filter(organization=user.organization)

        # Fallback: if no organization field is found, return empty or as-is?
        # Safety: If not superuser and no org filter possible, return none.
        return queryset.filter(organization=user.organization) 
