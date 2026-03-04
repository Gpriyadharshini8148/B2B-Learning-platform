from django.db import models
from .course import Course
from admin.access.models.base import BaseModel

class OrganizationCourse(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='organization_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='organization_courses')

    class Meta:
        db_table = 'courses_organizationcourse'

    def __str__(self):
        return f"{self.organization.name} - {self.course.title}"
