from django.db import models
from .enrollment import Enrollment
from admin.access.models.base import BaseModel

class Certificate(BaseModel):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_url = models.URLField()

    def __str__(self):
        return f"Certificate for {self.enrollment.user.email} - {self.enrollment.course.title}"
