from django.db import models
from admin.access.models.base import BaseModel
from .enrollment import Enrollment

class Certificate(BaseModel):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_url = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'enrollments_certificate'

    def __str__(self):
        return f"Certificate for {self.enrollment}"
