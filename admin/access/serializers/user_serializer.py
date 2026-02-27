from rest_framework import serializers
from ..models.user import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'organization', 'first_name', 'last_name', 'email', 'is_active', 'last_login', 'created_at')
        read_only_fields = ('created_at', 'last_login')
