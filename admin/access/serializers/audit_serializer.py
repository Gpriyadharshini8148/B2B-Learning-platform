from rest_framework import serializers
from ..models.audit_log import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ('id', 'organization', 'user', 'action', 'entity_type', 'entity_id', 'metadata', 'created_at')
        read_only_fields = ('id', 'created_at')
