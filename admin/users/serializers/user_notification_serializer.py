from rest_framework import serializers
from admin.access.models import UserNotification

class StudentNotificationSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='notification.title', read_only=True)
    message = serializers.CharField(source='notification.message', read_only=True)
    type = serializers.CharField(source='notification.type', read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'title', 'message', 'type', 'is_read', 'read_at', 'created_at']
