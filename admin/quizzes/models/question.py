from django.db import models
from .quiz import Quiz
from admin.access.models.base import BaseModel

class Question(BaseModel):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=50, choices=QUESTION_TYPES, default='multiple_choice')
    marks = models.IntegerField(default=1)

    def __str__(self):
        return self.text
