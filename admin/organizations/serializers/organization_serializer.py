from rest_framework import serializers
from ..models.organization import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'subdomain', 'industry', 'is_active', 'is_verified', 
            'approval_status', 'approval_token', 'email', 'website', 'logo', 
            'description', 'created_at', 'updated_at'
        )
        read_only_fields = ['id', 'created_at', 'updated_at', 'approval_token']

    def validate_subdomain(self, value):
        if not value.isalnum():
            # Allow hyphens but must be alphanumeric mostly
            if not all(c.isalnum() or c == '-' for c in value):
                raise serializers.ValidationError("Subdomain must be alphanumeric and can contain hyphens.")
        return value.lower()

    def validate_email(self, value):
        if value and not value.endswith(('.com', '.org', '.net', '.edu', '.in')):
             # Simple example validation
             pass
        return value

    def to_representation(self, instance):
        """
        In the representation, we want the logo field to show the image details/URL 
        even if it's stored as an ID reference.
        """
        representation = super().to_representation(instance)
        if instance.logo:
            # Inject full image details including URL
            logo_data = {
                "id": instance.logo.id,
                "image_id": instance.logo.image_id,
                "url": instance.logo.image_file.url if instance.logo.image_file else None
            }
            representation['logo'] = logo_data
        return representation
