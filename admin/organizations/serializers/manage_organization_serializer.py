from rest_framework import serializers

class ManageOrganizationListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    subdomain = serializers.CharField()
    status = serializers.CharField()

class ManageOrganizationCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    subdomain = serializers.CharField()
    email = serializers.EmailField()
