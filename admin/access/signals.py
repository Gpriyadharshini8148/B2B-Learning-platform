from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models.user import User
from .models.enrollment import Enrollment
from .models.course_progress import CourseProgress
from .models.lesson_progress import LessonProgress
from .models.lesson import Lesson
from concurrent.futures import ThreadPoolExecutor

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

    if subject and message and recipient_email:
        executor = ThreadPoolExecutor(max_workers=1)
        
        def send_background_email(subj, msg, from_email, recipient):
            try:
                send_mail(subj, msg, from_email, [recipient], fail_silently=False)
            except Exception as e:
                print(f"Failed to send email: {e}")
        
        executor.submit(send_background_email, subject, message, settings.DEFAULT_FROM_EMAIL, recipient_email)

@receiver(post_save, sender=Enrollment)
def create_initial_progress(sender, instance, created, **kwargs):
    """
    Automatically create CourseProgress and LessonProgress records
    when a new Enrollment is created.
    """
    if created:
        # 1. Create CourseProgress (Overall % tracker)
        CourseProgress.objects.get_or_create(enrollment=instance)

        # 2. Create LessonProgress entries for every lesson in this course
        lessons = Lesson.objects.filter(section__course=instance.course)
        for lesson in lessons:
            LessonProgress.objects.get_or_create(
                enrollment=instance,
                lesson=lesson
            )

@receiver(post_save, sender=LessonProgress)
def update_course_progress(sender, instance, **kwargs):
    """
    Update CourseProgress percentage when a LessonProgress is saved.
    """
    enrollment = instance.enrollment
    course = enrollment.course
    
    # Total lessons in the course
    total_lessons = Lesson.objects.filter(section__course=course).count()
    
    if total_lessons > 0:
        # Number of completed lessons for this enrollment
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
        else:
            progress.completed_at = None
            
        progress.save()
