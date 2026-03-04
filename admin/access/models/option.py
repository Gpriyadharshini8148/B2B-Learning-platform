from django.db import models
from .question import Question
from admin.access.models.base import BaseModel

class Option(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='options', null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'quizzes_option'

    def __str__(self):
        return self.text
