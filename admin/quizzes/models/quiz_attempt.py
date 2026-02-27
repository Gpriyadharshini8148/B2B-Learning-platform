from django.db import models
from admin.access.models.user import User
from .quiz import Quiz
from admin.access.models.base import BaseModel

class QuizAttempt(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.quiz.title} Attempt"
