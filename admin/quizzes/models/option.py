from django.db import models
from .question import Question
from admin.access.models.base import BaseModel
from admin.organizations.models.organization import Organization

class Option(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='options', null=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
