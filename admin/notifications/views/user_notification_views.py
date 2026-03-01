from rest_framework import viewsets
from ..models.user_notification import UserNotification
from ..serializers.user_notification_serializer import UserNotificationSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin

class UserNotificationViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = UserNotificationSerializer

    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user
        )
