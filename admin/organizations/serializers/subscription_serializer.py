from rest_framework import serializers
from admin.access.models.subscription import Subscription

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('id', 'plan_name', 'end_date', 'organization')
