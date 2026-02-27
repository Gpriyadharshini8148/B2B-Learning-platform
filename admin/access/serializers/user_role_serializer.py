from rest_framework import serializers
from ..models.user_role import UserRole

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = '__all__'
