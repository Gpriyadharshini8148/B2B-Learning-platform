from rest_framework import serializers
from admin.access.models.user_department import UserDepartment

class UserDepartmentSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = UserDepartment
        fields = ('id', 'user', 'user_email', 'department', 'department_name')
