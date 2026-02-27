from rest_framework import viewsets
from ..models.notification import Notification
from ..serializers.notification_serializer import NotificationSerializer
from ...access.permissions.tenant_permissions import TenantSafeViewSetMixin

class NotificationViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    model = Notification
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
