from django.db import models
from .course import Course
from admin.access.models.base import BaseModel

class Section(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='sections', null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    order_number = models.IntegerField()

    class Meta:
        db_table = 'courses_section'

    def __str__(self):
        return f"{self.course.title} - {self.title}"
