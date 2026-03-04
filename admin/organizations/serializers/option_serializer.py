from rest_framework import serializers
from admin.access.models import Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'is_correct', 'organization', 'question')
        read_only_fields = ('id', 'organization', 'question')
