from rest_framework import serializers

class InviteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.CharField(required=False, default='learner')

class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=True)
