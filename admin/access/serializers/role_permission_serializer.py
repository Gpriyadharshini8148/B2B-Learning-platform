from rest_framework import serializers
from ..models.role_permission import RolePermission

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'
