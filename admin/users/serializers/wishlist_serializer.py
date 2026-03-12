from rest_framework import serializers
from admin.access.models import Wishlist

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'course', 'created_at']
        read_only_fields = ['user', 'created_at']
