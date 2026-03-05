from django.contrib import admin
from django.apps import apps
from .models.user import User
from .models.role import Role
from .models.user_role import UserRole
from .models.course import Course
from .models.enrollment import Enrollment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'organization', 'approval_status', 'is_active', 'is_superuser')
    list_filter = ('approval_status', 'is_active', 'is_superuser', 'organization')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'description')
    search_fields = ('name',)

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'created_at')
    list_filter = ('organization',)
    search_fields = ('title',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'created_at')
    list_filter = ('status', 'course__organization')

# Fallback for all other models in the 'access' app
all_models = apps.get_app_config('access').get_models()
for model in all_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
