from rest_framework import serializers
from ..models.organization_sso import OrganizationSSO

class OrganizationSSOSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSSO
        fields = ('id', 'organization', 'provider', 'client_id', 'client_secret', 'metadata_url')
