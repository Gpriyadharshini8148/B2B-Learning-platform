from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.subscription_views import SubscriptionViewSet
from .views.payment_views import PaymentViewSet

router = DefaultRouter()
router.register('list', SubscriptionViewSet, basename='subscription')
router.register('payments', PaymentViewSet, basename='payment')

@api_view(['GET'])
def sub_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
        'payments': request.build_absolute_uri('payments/'),
    })

urlpatterns = [
    path('', sub_root, name='sub-root'),
    path('', include(router.urls)),
]
