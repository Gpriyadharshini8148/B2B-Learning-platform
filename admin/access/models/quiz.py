from django.db import models
from admin.access.models.base import BaseModel

class Quiz(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='quizzes', null=True)
    course = models.ForeignKey('access.Course', on_delete=models.CASCADE, related_name='quizzes')
    lesson = models.ForeignKey('access.Lesson', on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    passing_score = models.FloatField(default=50.0)

    class Meta:
        db_table = 'quizzes_quiz'

    def __str__(self):
        return self.title
