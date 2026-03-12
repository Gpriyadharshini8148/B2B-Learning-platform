from django.urls import path, include
from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .views.user_views import UserViewSet
from .views.role_views import RoleViewSet
from .views.permission_views import PermissionViewSet
from .views.audit_views import AuditViewSet
from .authentication.views import KeycloakTokenObtainPairView
from .authentication.refresh_views import KeycloakTokenRefreshView
from .views.signup_views import OrganizationSignupView, UserSignupView
from .views.otp_views import VerifyOTPView
from .views.logout_views import LogoutView
from .views.dashboard_views import UserDashboardView
from .views.password_views import ResetPasswordView
from .views.image_views import ImageViewSet
from .views.certificate_views import VerifyCertificateView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'audit-logs', AuditViewSet, basename='auditlog')
router.register(r'images', ImageViewSet, basename='image')

@extend_schema(responses={200: dict})
@api_view(['GET'])
def access_root(request):

    """
    Overview of Authentication and Access endpoints.
    """
    urls = {
        'login': request.build_absolute_uri('auth/login/'),
        'organization-signup': request.build_absolute_uri('signup/organization/'),
        'user-signup': request.build_absolute_uri('signup/user/'),
        'verify-otp': request.build_absolute_uri('verify-otp/'),
    }

    super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

    if request.user and request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'email', '') == super_admin_email):
        urls['users-list'] = request.build_absolute_uri('users/')
        urls['roles-list'] = request.build_absolute_uri('roles/')
        urls['audit-logs'] = request.build_absolute_uri('audit-logs/')

    return Response(urls)

urlpatterns = [
    path('', access_root, name='access-root'),
    path('', include(router.urls)),
    
    # Signup endpoints
    path('signup/organization/', OrganizationSignupView.as_view(), name='org-signup'),
    path('signup/user/', UserSignupView.as_view(), name='user-signup'),
    path('user/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    
    # Auth endpoints
    path('auth/login/', KeycloakTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', KeycloakTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # Dashboard endpoint
    path('dashboard/', UserDashboardView.as_view(), name='dashboard'),
    
    # Password endpoint
    path('auth/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Secure Certificate Verification
    path('certificates/verify/', VerifyCertificateView.as_view(), name='verify-certificate'),
]
