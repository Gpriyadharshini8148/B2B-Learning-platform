from rest_framework import serializers

class WishlistToggleSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
