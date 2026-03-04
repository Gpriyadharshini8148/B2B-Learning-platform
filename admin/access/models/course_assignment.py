from django.db import models
from admin.access.models.user import User
from admin.access.models.course import Course
from admin.access.models.base import BaseModel

class CourseAssignment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_courses')
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'enrollments_courseassignment'

    def __str__(self):
        return f"Assigned: {self.course.title} to {self.user.email}"
