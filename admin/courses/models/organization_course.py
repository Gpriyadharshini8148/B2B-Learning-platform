from django.db import models
from admin.organizations.models.organization import Organization
from .course import Course
from admin.access.models.base import BaseModel

class OrganizationCourse(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='organization_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='organization_courses')

    def __str__(self):
        return f"{self.organization.name} - {self.course.title}"
