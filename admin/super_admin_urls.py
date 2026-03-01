from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admin.organizations.views.manage_organization_api import ManageOrganizationsViewSet

router = DefaultRouter()
router.register('manage_organizations', ManageOrganizationsViewSet, basename='manage-org')

urlpatterns = [
    path('', include(router.urls)),
]
