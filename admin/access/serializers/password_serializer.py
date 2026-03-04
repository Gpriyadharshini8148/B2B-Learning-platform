from rest_framework import serializers

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    password = serializers.CharField(required=True)
