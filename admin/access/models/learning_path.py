from django.db import models
from admin.access.models.user import User
from admin.access.models.base import BaseModel

class LearningPath(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='learning_paths', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'courses_learningpath'

    def __str__(self):
        return self.name
