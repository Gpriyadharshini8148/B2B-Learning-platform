from rest_framework import viewsets
from ..models.subscription import Subscription
from ..serializers.subscription_serializer import SubscriptionSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class SubscriptionViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Subscription
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
