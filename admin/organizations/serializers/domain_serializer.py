from rest_framework import serializers
from ..models.organization_domain import OrganizationDomain

class OrganizationDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationDomain
        fields = '__all__'
