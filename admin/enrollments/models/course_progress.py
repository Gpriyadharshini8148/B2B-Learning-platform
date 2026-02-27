from django.db import models
from .enrollment import Enrollment
from admin.access.models.base import BaseModel

class CourseProgress(BaseModel):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    progress_percentage = models.FloatField(default=0.0)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.enrollment.course.title} Progress: {self.progress_percentage}%"
