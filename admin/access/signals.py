from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models.user import User

@receiver(post_save, sender=User)
def send_user_approval_email(sender, instance, created, **kwargs):
    if getattr(instance, '_skip_signal', False):
        return

    if created and instance.approval_status == 'pending':
        # Determine recipient and message
        is_signup = getattr(instance, '_is_signup', False)
        
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/user/{instance.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/user/{instance.approval_token}/reject/"
        
        if is_signup:
            # Send to Organization Admin
            subject = "New Learner Signup: Approval Required"
            recipient_email = None
            
            # Find the admin of this organization (usually the owner/first user)
            admin_user = User.objects.filter(organization=instance.organization).exclude(id=instance.id).first()
            if admin_user:
                recipient_email = admin_user.email
            else:
                # Fallback to super admin if no org admin found
                recipient_email = settings.EMAIL_HOST_USER
            
            message = (
                f"A new learner '{instance.email}' has requested to join your organization '{instance.organization.name}'.\n\n"
                f"Please click the link below to approve or reject this request:\n\n"
                f"Accept: {accept_link}\n"
                f"Reject: {reject_link}\n\n"
                f"If approved, the learner will be notified that they can log in."
            )
        else:
            # Bulk Import - Send to the User themselves
            subject = "Action Required: Approve your User Account"
            recipient_email = instance.email
            message = (
                f"Super admin creates your user account '{instance.email}' expect for acceptance.\n\n"
                f"Please click the link below to accept or reject this account:\n\n"
                f"Accept: {accept_link}\n"
                f"Reject: {reject_link}\n\n"
                "Once approved, you can proceed with login with your mail and password."
            )
        
        if recipient_email:
            from concurrent.futures import ThreadPoolExecutor
            executor = ThreadPoolExecutor(max_workers=1)
            
            def send_background_email(subj, msg, from_email, recipient):
                try:
                    send_mail(subj, msg, from_email, [recipient], fail_silently=False)
                except Exception as e:
                    print(f"Failed to send email: {e}")
            
            executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, recipient_email)

