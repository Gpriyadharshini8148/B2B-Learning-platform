from rest_framework import serializers
from ..models.user import User

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    subdomain = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'subdomain', 'status', 'email', 'is_active', 'last_login', 'created_at', 'organization', 'first_name', 'last_name')
        read_only_fields = ('created_at', 'last_login')

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_subdomain(self, obj):
        return obj.organization.subdomain if obj.organization else None

    def get_status(self, obj):
        return "active" if obj.is_active else "inactive"
