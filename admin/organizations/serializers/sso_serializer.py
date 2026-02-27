from rest_framework import serializers
from ..models.organization_sso import OrganizationSSO

class OrganizationSSOSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSSO
        fields = '__all__'
