from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.subscription_views import SubscriptionViewSet

router = DefaultRouter()
router.register('list', SubscriptionViewSet, basename='subscription')

@api_view(['GET'])
def sub_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
    })

urlpatterns = [
    path('', sub_root, name='sub-root'),
    path('', include(router.urls)),
]
