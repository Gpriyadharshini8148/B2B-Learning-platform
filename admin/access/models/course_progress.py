from django.db import models
from admin.access.models.base import BaseModel
from .enrollment import Enrollment

class CourseProgress(BaseModel):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='progress')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'enrollments_courseprogress'

    def __str__(self):
        return f"Progress for {self.enrollment}: {self.progress_percentage}%"
