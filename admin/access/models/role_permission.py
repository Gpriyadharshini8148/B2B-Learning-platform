from django.db import models
from .role import Role
from .permission import Permission
from .base import BaseModel

class RolePermission(BaseModel):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.role} - {self.permission}"