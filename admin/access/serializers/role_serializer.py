from rest_framework import serializers
from ..models.role import Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'organization', 'name', 'description')
