from rest_framework import serializers
from admin.access.models.department import Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('id', 'name', 'organization')
