from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views.user_views import UserViewSet
from .views.role_views import RoleViewSet
from .views.permission_views import PermissionViewSet
from .views.audit_views import AuditLogViewSet
from .authentication.views import CustomTokenObtainPairView
from .views.signup_views import OrganizationSignupView, LearnerSignupView
from .views.otp_views import VerifyOTPView
from .views.logout_views import LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'audit-logs', AuditLogViewSet, basename='auditlog')

@api_view(['GET'])
def access_root(request):
    """
    Overview of Authentication and Access endpoints.
    """
    urls = {
        'login': request.build_absolute_uri('auth/login/'),
        'token-refresh': request.build_absolute_uri('auth/refresh/'),
        'token-verify': request.build_absolute_uri('auth/verify/'),
        'organization-signup': request.build_absolute_uri('signup/organization/'),
        'learner-signup': request.build_absolute_uri('signup/learner/'),
        'verify-otp': request.build_absolute_uri('verify-otp/'),
    }

    if request.user and request.user.is_authenticated and request.user.is_superuser:
        urls['users-list'] = request.build_absolute_uri('users/')
        urls['roles-list'] = request.build_absolute_uri('roles/')
        urls['audit-logs'] = request.build_absolute_uri('audit-logs/')

    return Response(urls)

urlpatterns = [
    path('', access_root, name='access-root'),
    path('', include(router.urls)),
    
    # Signup endpoints
    path('signup/organization/', OrganizationSignupView.as_view(), name='org-signup'),
    path('signup/learner/', LearnerSignupView.as_view(), name='learner-signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Auth endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
