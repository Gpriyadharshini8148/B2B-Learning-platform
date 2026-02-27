from rest_framework import serializers
from ..models.user_department import UserDepartment

class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        fields = '__all__'
