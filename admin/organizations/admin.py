from django.contrib import admin
from django.apps import apps
from .models.organization import Organization
from .models.invitation import Invitation

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'approval_status', 'is_active', 'is_verified', 'created_at')
    list_filter = ('approval_status', 'is_active', 'is_verified')
    search_fields = ('name', 'subdomain', 'email')
    ordering = ('-created_at',)

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'organization', 'role', 'is_used', 'expires_at')
    list_filter = ('is_used', 'organization')
    search_fields = ('email',)

# Fallback for all other models in the 'organizations' app
all_models = apps.get_app_config('organizations').get_models()
for model in all_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
