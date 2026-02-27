from django.db import models
from admin.access.models.base import BaseModel

class Skill(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
