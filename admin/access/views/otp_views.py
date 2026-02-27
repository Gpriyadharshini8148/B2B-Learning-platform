from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.access.authentication.serializers import VerifyOTPSerializer

class VerifyOTPView(views.APIView):
    """
    Verifies the 6-digit OTP stored on the User model.
    Updates the status to 'pending' if OTP matches.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=VerifyOTPSerializer)
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find the user awaiting OTP verification
            user = User.objects.get(
                email=email, 
                otp=otp, 
                approval_status='pending_otp'
            )

            # OTP is correct! Clear it.
            user.otp = None

            # If this was the first user of a new organization, update the org status too
            org = user.organization
            if org and getattr(org, 'approval_status', '') == 'pending_otp':
                user.approval_status = 'pending'
                user.save()
                org.approval_status = 'pending'
                org.save()
                
                # Notify Super Admin about the new Organization request
                self.notify_super_admin(org)
            else:
                # It's a user signup. Instantly approve them to allow login.
                user.approval_status = 'approved'
                user.is_active = True
                user.is_verified = True
                user.save()

            return Response({"message": "otp verification successfully"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "invalid otp"}, status=status.HTTP_400_BAD_REQUEST)

    def notify_super_admin(self, org):
        super_admin_email = settings.EMAIL_HOST_USER
        
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/reject/"

        subject = f"NEW REGISTRATION REQUEST: {org.name}"
        message = (
            f"Hello Super Admin,\n\n"
            f"A new organization has verified their email and requested to join:\n\n"
            f"Organization: {org.name}\n"
            f"Subdomain: {org.subdomain}\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )
        self.send_email_in_background(subject, message, super_admin_email)

    def notify_org_admin(self, user):
        # Notify the Org Admin that a new user is waiting
        admin_user = User.objects.filter(organization=user.organization).exclude(id=user.id).first()
        recipient_email = admin_user.email if admin_user else settings.EMAIL_HOST_USER
        
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/user/{user.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/user/{user.approval_token}/reject/"
        
        subject = "New User Signup: Approval Required"
        message = (
            f"A new user '{user.email}' has verified their email and wants to join your organization '{user.organization.name}'.\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )
        self.send_email_in_background(subject, message, recipient_email)

    def send_email_in_background(self, subject, message, recipient_list):
        from concurrent.futures import ThreadPoolExecutor
        executor = ThreadPoolExecutor(max_workers=1)
        
        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                print(f"Failed to send email to Super Admin: {e}")
                
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
