from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.notification_views import NotificationViewSet
from .views.user_notification_views import UserNotificationViewSet

router = DefaultRouter()
router.register('list', NotificationViewSet, basename='notification')
router.register('user-notifications', UserNotificationViewSet, basename='user-notification')

@api_view(['GET'])
def notif_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
        'user-notifications': request.build_absolute_uri('user-notifications/'),
    })

urlpatterns = [
    path('', notif_root, name='notif-root'),
    path('', include(router.urls)),
]
