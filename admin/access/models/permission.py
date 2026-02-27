from django.db import models
from .base import BaseModel

class Permission(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name