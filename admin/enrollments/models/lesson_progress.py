from django.db import models
from .enrollment import Enrollment
from admin.courses.models.lesson import Lesson
from admin.access.models.base import BaseModel

class LessonProgress(BaseModel):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watch_time_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.lesson.title}"
