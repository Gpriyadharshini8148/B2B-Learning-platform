from rest_framework import serializers
from admin.access.models import Option

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct", "question"]
        read_only_fields = ["id"]
