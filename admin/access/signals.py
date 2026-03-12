from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models.user import User
from .models.enrollment import Enrollment
from .models.course_progress import CourseProgress
from .models.lesson_progress import LessonProgress
from .models.lesson import Lesson
from .models.certificate import Certificate
from django.core import signing
from django.core.signing import TimestampSigner
from concurrent.futures import ThreadPoolExecutor

# Global executor for background emails
executor = ThreadPoolExecutor(max_workers=5)

def send_background_email(subject, message, from_email, recipient_email):
    """ Helper to send emails in a background thread. """
    try:
        send_mail(subject, message, from_email, [recipient_email], fail_silently=False)
    except Exception as e:
        print(f"Error sending background email to {recipient_email}: {e}")

def create_initial_progress_task(enrollment_id):
    """Background task to create initial progress for a newly enrolled user."""
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        # 1. Create CourseProgress (Overall % tracker)
        CourseProgress.objects.get_or_create(enrollment=enrollment)

        # 2. Create LessonProgress entries for every lesson in this course
        lessons = Lesson.objects.filter(section__course=enrollment.course)
        for lesson in lessons:
            LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
    except Exception as e:
         print(f"Error in create_initial_progress_task for enrollment {enrollment_id}: {e}")

def update_course_progress_task(enrollment_id):
    """Background task to update course progress percentage."""
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        course = enrollment.course
        
        # Total lessons in the course
        total_lessons = Lesson.objects.filter(section__course=course).count()
        
        if total_lessons > 0:
            # Number of completed lessons for this enrollment
            # IMPORTANT: Re-import inside if necessary for threads
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment, 
                is_completed=True
            ).count()
            
            progress_percentage = (completed_lessons / total_lessons) * 100
            
            # Update or create the course progress
            progress, _ = CourseProgress.objects.get_or_create(enrollment=enrollment)
            progress.progress_percentage = round(progress_percentage, 2)
            
            if progress_percentage >= 100:
                progress.completed_at = timezone.now()
                
                # Auto-generate secure signed certificate
                token = signing.dumps({'enrollment_id': enrollment.id})
                secure_url = f"/api/access/certificates/verify/?token={token}"
                
                Certificate.objects.get_or_create(
                    enrollment=enrollment,
                    defaults={
                        'certificate_url': secure_url
                    }
                )
                
                # Mark enrollment as completed
                if enrollment.status != 'completed':
                    enrollment.status = 'completed'
                    enrollment.save(update_fields=['status'])
            else:
                progress.completed_at = None
                
                # Clean up certificate if progress drops below 100
                Certificate.objects.filter(enrollment=enrollment).delete()
                if enrollment.status == 'completed':
                    enrollment.status = 'active'
                    enrollment.save(update_fields=['status'])
                
            progress.save()
    except Exception as e:
         print(f"Error in update_course_progress_task for enrollment {enrollment_id}: {e}")

# Custom signals for events that don't result in immediate DB records
organization_provisioned = Signal() # Sent by Super Admin Provisioning View
organization_requested = Signal()   # Sent by Public Org Signup View

@receiver(post_save, sender=User)
def send_user_approval_email(sender, instance, created, **kwargs):
    if getattr(instance, '_skip_signal', False):
        return

    subject = None
    message = None
    recipient_email = None

    if instance.approval_status == 'pending_otp' and getattr(instance, '_is_signup', False):
        # 1. User Signup - Send OTP
        org_name = f"'{instance.organization.name}'" if instance.organization else "our platform"
        subject = "Your Registration OTP"
        message = (
            f"Hello,\n\n"
            f"Your OTP for registering at {org_name} is:\n"
            f"{instance.otp}\n\n"
            f"Please use this OTP to verify your account.\n"
        )
        recipient_email = instance.email

    elif created and instance.approval_status == 'pending' and getattr(instance, '_is_org_signup', False):
        # 2. Organization Signup - Notify Super Admin
        org = instance.organization
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/org/{org.approval_token}/reject/"

        subject = f"NEW REGISTRATION REQUEST: {org.name}"
        message = (
            f"Hello Super Admin,\n\n"
            f"A new organization has requested to join:\n\n"
            f"Organization: {org.name}\n"
            f"Subdomain: {org.subdomain}\n\n"
            f"Accept: {accept_link}\n"
            f"Reject: {reject_link}\n"
        )
        recipient_email = settings.EMAIL_HOST_USER

    elif created and instance.approval_status == 'pending':
        # 3. Standard Approval or Bulk Import logic
        accept_link = f"http://localhost:8000/api/bulk-cms/approve/user/{instance.approval_token}/accept/"
        reject_link = f"http://localhost:8000/api/bulk-cms/approve/user/{instance.approval_token}/reject/"
        
        is_signup = getattr(instance, '_is_signup', False)
        if is_signup:
            # Send to Organization Admin
            subject = "New User Signup: Approval Required"
            admin_user = User.objects.filter(organization=instance.organization).exclude(id=instance.id).first()
            recipient_email = admin_user.email if admin_user else settings.EMAIL_HOST_USER
            org_name = f"'{instance.organization.name}'" if instance.organization else "our platform"
            message = (
                f"A new user '{instance.email}' has requested to join {org_name}.\n\n"
                f"Please click the link below to approve or reject this request:\n\n"
                f"Accept: {accept_link}\n"
                f"Reject: {reject_link}\n\n"
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

    elif instance.approval_status == 'approved' and not instance.password_hash:
        # 4. User Approved but no password (e.g. Admin creation) - Send Reset Password link
        signer = TimestampSigner()
        token = signer.sign(instance.email)
        
        # Use a base URL (hardcoded localhost for now as per project convention)
        reset_url = f"http://localhost:8000/api/access/auth/reset-password/?token={token}"
        
        subject = "Account Approved: Set Your Password"
        message = (
            f"Hello {instance.first_name or 'there'},\n\n"
            f"Your account for '{instance.organization.name if instance.organization else 'our platform'}' has been approved.\n\n"
            f"Please click the link below to set your password and access your account:\n"
            f"{reset_url}\n\n"
            "Welcome aboard!"
        )
        recipient_email = instance.email

    # Send the email if any of the conditions above were met and set the variables
    if subject and message and recipient_email:
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, recipient_email)

@receiver(organization_provisioned)
def on_organization_provisioned(sender, **kwargs):
    """
    Handles email for Super Admin organization provisioning (Deferred Creation).
    """
    request = kwargs.get('request')
    email = kwargs.get('email')
    org_name = kwargs.get('name')
    subdomain = kwargs.get('subdomain')

    provisioning_data = {
        'type': 'new_organization_setup',
        'name': org_name,
        'subdomain': subdomain,
        'email': email
    }
    token = signing.dumps(provisioning_data)
    base_url = f"{request.scheme}://{request.get_host()}"
    setup_url = f"{base_url}/api/access/auth/reset-password/?token={token}"

    subject = f"Welcome to Udemy Clone: Your account for {org_name} is ready!"
    message = (
        f"Hello,\n\n"
        f"An organization account has been created for '{org_name}' on our platform.\n"
        f"You have been assigned as the administrator.\n\n"
        f"Please click the link below to set up your account and password:\n"
        f"{setup_url}\n\n"
        f"Welcome aboard!\n"
    )

    executor.submit(send_mail, subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)

@receiver(organization_requested)
def on_organization_requested(sender, **kwargs):
    """
    Handles email for Public Organization Signup requests (Sent to Super Admin).
    """
    request = kwargs.get('request')
    email = kwargs.get('email')
    org_name = kwargs.get('name')
    subdomain = kwargs.get('subdomain')
    password = kwargs.get('password')

    data = {
        'name': org_name,
        'subdomain': subdomain,
        'email': email,
        'password': password
    }
    token = signing.dumps(data)
    
    accept_link = f"http://localhost:8000/api/bulk-cms/approve/org/{token}/accept/"
    reject_link = f"http://localhost:8000/api/bulk-cms/approve/org/{token}/reject/"

    subject = f"NEW REGISTRATION REQUEST: {org_name}"
    message = (
        f"Hello Super Admin,\n\n"
        f"A new organization has requested to join:\n\n"
        f"Organization: {org_name}\n"
        f"Subdomain: {subdomain}\n"
        f"Admin Email: {email}\n\n"
        f"Click here to Accept and Provision: {accept_link}\n"
        f"Click here to Reject: {reject_link}\n"
    )

    executor.submit(send_mail, subject, message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER], fail_silently=False)

@receiver(post_save, sender=Enrollment)
def create_initial_progress(sender, instance, created, **kwargs):
    """
    Automatically create CourseProgress and LessonProgress records
    when a new Enrollment is created.
    """
    if created:
        executor.submit(create_initial_progress_task, instance.id)

@receiver(post_save, sender=LessonProgress)
def update_course_progress(sender, instance, **kwargs):
    executor.submit(update_course_progress_task, instance.enrollment.id)
