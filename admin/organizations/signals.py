from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models.organization import Organization
from .models.invitation import Invitation
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Organization)
def send_organization_approval_email(sender, instance, created, **kwargs):
    """
    Sends an approval email to the first user/admin when an Organization is created in pending status.
    """
    if created and instance.approval_status == 'pending':
        subject = "Action Required: Approve your Organization Account"
        
        accept_link = f"http://localhost:8000/api/admin/bulk-cms/approve/org/{instance.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/admin/bulk-cms/approve/org/{instance.approval_token}/reject/"
        
        message = (
            f"Super admin creates your organization '{instance.name}' expect for acceptance.\n\n"
            f"Please click the link below to accept or reject this account:\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n\n"
            "Once approved, you can proceed with login with your mail and password."
        )
        
        try:
            admin_user = instance.users.first()
            if admin_user:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_user.email],
                    fail_silently=False,
                )
        except Exception as e:
            logger.error(f"Failed to send organization approval email: {e}")

from django.core import signing

@receiver(post_save, sender=Invitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Sends a secure invitation email when a new Invitation is created.
    """
    if created:
        # Build the same token logic that was in the view
        token_data = {
            'invitation_id': str(instance.token),
            'email': instance.email,
            'org_id': instance.organization.pk,
            'role': instance.role,
        }
        signed_token = signing.dumps(token_data)

        # Assuming the request host is needed, we usually handle this by using 
        # a settings variable or passing context. For simplicity in a local dev,
        # we'll use localhost:8000.
        base_url = "http://localhost:8000"
        accept_url = f"{base_url}/api/organizations/accept-invite/?token={signed_token}"

        subject = f"You're invited to join {instance.organization.name}!"
        message = (
            f"Hello,\n\n"
            f"You have been invited to join "
            f"'{instance.organization.name}' as a '{instance.role}'.\n\n"
            f"Please click the link below to set up your account:\n"
            f"{accept_url}\n\n"
            f"This link will expire in 7 days.\n"
        )

        try:
            executor = ThreadPoolExecutor(max_workers=1)
            executor.submit(send_mail, subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)
        except Exception as e:
            logger.error(f"Failed to initiate background email for invitation: {e}")
