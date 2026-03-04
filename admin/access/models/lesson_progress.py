from django.db import models
from admin.access.models.base import BaseModel
from .enrollment import Enrollment
from .lesson import Lesson

class LessonProgress(BaseModel):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    watch_time_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = 'enrollments_lessonprogress'
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f"Progress for {self.enrollment} on {self.lesson.title}: {'Completed' if self.is_completed else 'In Progress'}"
