from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models import UserNotification
from ..serializers.user_notification_serializer import StudentNotificationSerializer
from django.utils import timezone

class StudentNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/user/notifications
    GET /api/user/notifications/unread-count
    PUT /api/user/notifications/{id}/read
    PUT /api/user/notifications/read-all
    """
    serializer_class = StudentNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserNotification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"unread_count": count})

    @action(detail=True, methods=['put'])
    def read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({"message": "Notification marked as read"})

    @action(detail=False, methods=['put'], url_path='read-all')
    def read_all(self, request):
        self.get_queryset().filter(is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
        return Response({"message": "All notifications marked as read"})
