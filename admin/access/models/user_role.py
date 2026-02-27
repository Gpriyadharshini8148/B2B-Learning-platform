from django.db import models
from .base import BaseModel

class UserRole(BaseModel):
    user = models.ForeignKey('access.User', on_delete=models.CASCADE)
    role = models.ForeignKey('access.Role', on_delete=models.CASCADE)

