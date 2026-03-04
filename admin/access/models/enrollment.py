from django.db import models
from admin.access.models.user import User
from admin.access.models.course import Course
from admin.access.models.base import BaseModel

class Enrollment(BaseModel):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')

    class Meta:
        db_table = 'enrollments_enrollment'

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
