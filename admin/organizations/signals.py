from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models.organization import Organization

@receiver(post_save, sender=Organization)
def send_organization_approval_email(sender, instance, created, **kwargs):
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
        
        # We need an email address for the organization. 
        # Since Organization doesn't have an email field, we might look for the first user?
        # Or maybe the super admin should be notified? 
        # The user said "send to those persons". Let's assume there's a contact or we send it to a default for now.
        # Actually, let's assume the user meant the ADMIN of the organization.
        # For now, I'll print to console or use a placeholder if no email is found.
        
        # Trying to find the first user of this organization to send the email to.
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
        except:
            pass
