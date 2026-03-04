from rest_framework import serializers
from admin.access.models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'type')
        read_only_fields = ['organization']
