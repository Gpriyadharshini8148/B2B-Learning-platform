from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.organization_views import OrganizationViewSet
from .views.domain_views import DomainViewSet
from .views.sso_views import SSOViewSet
from .views.invitation_views import InviteUserView, AcceptInvitationView

router = DefaultRouter()
router.register('profile', OrganizationViewSet, basename='organization')
router.register('domains', DomainViewSet, basename='domain')
router.register('sso', SSOViewSet, basename='sso')

@api_view(['GET'])
def org_root(request):
    return Response({
        'profile': request.build_absolute_uri('profile/'),
        'domains': request.build_absolute_uri('domains/'),
        'sso': request.build_absolute_uri('sso/'),
    })

urlpatterns = [
    path('', org_root, name='org-root'),
    path('', include(router.urls)),
    path('invite/', InviteUserView.as_view(), name='invite-user'),
    path('accept-invite/', AcceptInvitationView.as_view(), name='accept-invite'),
]
