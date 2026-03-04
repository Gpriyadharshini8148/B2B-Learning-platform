from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admin.organizations.views.manage_organization_api import ManageOrganizationsViewSet
from admin.organizations.views.notification_api import SuperAdminNotificationViewSet

router = DefaultRouter()
router.register('manage_organizations', ManageOrganizationsViewSet, basename='manage-org')
router.register('global-notifications', SuperAdminNotificationViewSet, basename='super-admin-notifications')

urlpatterns = [
    path('', include(router.urls)),
]
