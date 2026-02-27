import os

base_path = r"d:\Udemy\udemy\admin"

model_files = {
    "courses/models/category.py": """from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
""",
    "courses/models/course.py": """from django.db import models
from admin.access.models.user import User
from .category import Category

class Course(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=100)
    language = models.CharField(max_length=100)

    thumbnail_url = models.URLField(blank=True, null=True)
    is_global = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
""",
    "courses/models/organization_course.py": """from django.db import models
from admin.organizations.models.organization import Organization
from .course import Course

class OrganizationCourse(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='organization_courses')
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.organization.name} - {self.course.title}"
""",
    "courses/models/section.py": """from django.db import models
from .course import Course

class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order_number = models.IntegerField()

    def __str__(self):
        return f"{self.course.title} - {self.title}"
""",
    "courses/models/lesson.py": """from django.db import models
from .section import Section

class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)
    order_number = models.IntegerField()
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title
""",
    "courses/models/skill.py": """from django.db import models

class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
""",
    "courses/models/course_skill.py": """from django.db import models
from .course import Course
from .skill import Skill

class CourseSkill(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='course_skills')

    def __str__(self):
        return f"{self.course.title} - {self.skill.name}"
""",
    "courses/models/learning_path.py": """from django.db import models
from admin.organizations.models.organization import Organization
from admin.access.models.user import User

class LearningPath(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='learning_paths', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
""",
    "courses/models/learning_path_course.py": """from django.db import models
from .learning_path import LearningPath
from .course import Course

class LearningPathCourse(models.Model):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='path_courses')
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.learning_path.name} - {self.course.title}"
""",
    "enrollments/models/enrollment.py": """from django.db import models
from admin.access.models.user import User
from admin.courses.models.course import Course

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
""",
    "enrollments/models/lesson_progress.py": """from django.db import models
from .enrollment import Enrollment
from admin.courses.models.lesson import Lesson

class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watch_time_seconds = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.lesson.title}"
""",
    "enrollments/models/course_progress.py": """from django.db import models
from .enrollment import Enrollment

class CourseProgress(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    progress_percentage = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.course.title} Progress: {self.progress_percentage}%"
""",
    "enrollments/models/certificate.py": """from django.db import models
from .enrollment import Enrollment

class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_url = models.URLField()
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Certificate for {self.enrollment.user.email} - {self.enrollment.course.title}"
""",
    "enrollments/models/course_assignment.py": """from django.db import models
from admin.access.models.user import User
from admin.courses.models.course import Course

class CourseAssignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_courses')
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Assigned: {self.course.title} to {self.user.email}"
""",
    "quizzes/models/quiz.py": """from django.db import models
from admin.courses.models.course import Course

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    passing_score = models.FloatField(default=50.0)

    def __str__(self):
        return self.title
""",
    "quizzes/models/question.py": """from django.db import models
from .quiz import Quiz

class Question(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default='multiple_choice')
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.text
""",
    "quizzes/models/option.py": """from django.db import models
from .question import Question

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
""",
    "quizzes/models/quiz_attempt.py": """from django.db import models
from admin.access.models.user import User
from .quiz import Quiz

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} Attempt"
""",
    "subscriptions/models/subscription.py": """from django.db import models
from admin.organizations.models.organization import Organization

class Subscription(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=255)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.organization.name} - {self.plan_name}"
""",
    "subscriptions/models/payment.py": """from django.db import models
from .subscription import Subscription

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment {self.id} - {self.subscription.plan_name}"
""",
    "notifications/models/notification.py": """from django.db import models

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('course', 'Course'),
        ('assignment', 'Assignment'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
""",
    "notifications/models/user_notification.py": """from django.db import models
from admin.access.models.user import User
from .notification import Notification

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.notification.title}"
"""
}

for rel_path, content in model_files.items():
    full_path = os.path.join(base_path, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
        
print("Successfully generated all models in admin/ path!")
