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

@receiver(post_save, sender=Invitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Sends an invitation email when a new Invitation is created.
    """
    if created:
        # Base URL for invitation acceptance
        invite_url = f"http://localhost:8000/api/organizations/accept-invite/?token={instance.token}"
        
        subject = f"Invitation to join {instance.organization.name}"
        message = (
            f"You have been invited to join {instance.organization.name} as a {instance.role.capitalize()}.\n\n"
            f"Please click the link below to accept the invitation and set up your account:\n"
            f"Accept Invitation: {invite_url}\n\n"
            "This link will expire in 7 days."
        )
        
        try:
            executor = ThreadPoolExecutor(max_workers=1)
            
            def send_background_email(subj, msg, from_email, recipient):
                try:
                    send_mail(subj, msg, from_email, [recipient], fail_silently=False)
                except Exception as e:
                    logger.error(f"Failed to send invitation email: {e}")
            
            executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, instance.email)
        except Exception as e:
            logger.error(f"Failed to initiate background email for invitation: {e}")
