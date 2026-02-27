from django.db import models
from admin.courses.models.course import Course
from admin.access.models.base import BaseModel

class Quiz(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    passing_score = models.FloatField(default=50.0)

    def __str__(self):
        return self.title
