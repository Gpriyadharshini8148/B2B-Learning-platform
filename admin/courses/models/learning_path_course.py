from django.db import models
from .learning_path import LearningPath
from .course import Course
from admin.access.models.base import BaseModel

class LearningPathCourse(BaseModel):
    learning_path = models.ForeignKey(LearningPath, on_delete=models.CASCADE, related_name='path_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='path_courses')
    order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.learning_path.name} - {self.course.title}"
