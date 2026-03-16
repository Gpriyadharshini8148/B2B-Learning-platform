from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Sum
import razorpay
from admin.access.models import Subscription, Payment
from ..serializers.subscription_serializer import SubscriptionSerializer
from ..serializers.payment_serializer import PaymentSerializer
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.models.course import Course
from admin.access.models.enrollment import Enrollment
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class OrgSubscriptionViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific subscription management.
    Allows Org Admins to view and manage their subscription plans.
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Subscription.objects.all()
            
        return Subscription.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )


class OrgPaymentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific payment management for Razorpay subscriptions.
    Provides revenue analytics for the organization.
    """
    serializer_class = PaymentSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Payment.objects.all().select_related('organization', 'subscription')
            
        return Payment.objects.filter(
            organization=self.request.user.organization
        ).select_related('subscription')

    def perform_create(self, serializer):
        """
        Creates a Razorpay Order and initializes a Payment record.
        """
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        amount = int(float(serializer.validated_data.get('amount')) * 100) # paise
        
        try:
            razorpay_order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            
            serializer.save(
                organization=self.request.user.organization,
                razorpay_order_id=razorpay_order['id'],
                status='pending'
            )
        except Exception as e:
            raise Exception(f"Failed to create Razorpay order: {str(e)}")

    @action(detail=True, methods=['post'], url_path='verify')
    def verify_payment(self, request, pk=None):
        """
        Verify the Razorpay signature and complete the payment.
        """
        payment = self.get_object()
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_signature = request.data.get('razorpay_signature')
        
        if not all([razorpay_payment_id, razorpay_order_id, razorpay_signature]):
            return Response({"error": "Missing payment identification fields"}, status=status.HTTP_400_BAD_REQUEST)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        try:
            client.utility.verify_payment_signature(params_dict)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()
            return Response({"message": "Payment verified and completed successfully", "payment_status": "completed"}, status=status.HTTP_200_OK)
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response({"error": "Payment verification failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='revenue-analytics')
    def revenue_analytics(self, request):
        """
        Provides revenue analytics for the organization.
        """
        user = request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        is_super_admin = user.is_superuser or getattr(user, 'email', '') == super_admin_email

        if not is_super_admin:
            org = user.organization
            if not org:
                return Response({"error": "No organization associated with this admin"}, status=status.HTTP_400_BAD_REQUEST)
                
            completed_payments = Payment.objects.filter(organization=org, status='completed')
            all_payments = Payment.objects.filter(organization=org)
            
            return Response({
                'organization_name': org.name,
                'user_count': User.objects.filter(organization=org).count(),
                'course_count': Course.objects.filter(organization=org).count(),
                'enrollment_count': Enrollment.objects.filter(course__organization=org).count(),
                'total_revenue': completed_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
                'total_transactions': all_payments.count(),
                'completed_payments': completed_payments.count(),
                'pending_payments': all_payments.filter(status='pending').count(),
                'failed_payments': all_payments.filter(status='failed').count(),
            })

        # Super Admin Plattform Wide Analytics
        tenants_analytics = []
        all_orgs = Organization.objects.all()
        for org in all_orgs:
            org_payments = Payment.objects.filter(organization=org)
            comp_payments = org_payments.filter(status='completed')
            tenants_analytics.append({
                'organization_name': org.name,
                'subdomain': org.subdomain,
                'user_count': User.objects.filter(organization=org).count(),
                'total_revenue': comp_payments.aggregate(Sum('amount'))['amount__sum'] or 0,
                'completed_payments': comp_payments.count(),
                'total_transactions': org_payments.count()
            })

        all_completed = Payment.objects.filter(status='completed')
        platform_summary = {
            'total_organizations': all_orgs.count(),
            'total_users': User.objects.exclude(email=super_admin_email).count(),
            'total_courses': Course.objects.count(),
            'total_enrollments': Enrollment.objects.count(),
            'total_platform_revenue': all_completed.aggregate(Sum('amount'))['amount__sum'] or 0,
            'total_global_transactions': Payment.objects.count()
        }

        return Response({
            'organizations': tenants_analytics,
            'platform_total': platform_summary
        })
