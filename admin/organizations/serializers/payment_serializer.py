from rest_framework import serializers
from admin.access.models.payment import Payment

class PaymentSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    plan_name = serializers.CharField(source='subscription.plan_name', read_only=True)

    class Meta:
        model = Payment
        fields = ('id', 'amount', 'status', 'razorpay_order_id', 'organization', 'organization_name', 'subscription', 'plan_name')
        read_only_fields = ('status', 'razorpay_order_id')
