from django.db import models
from admin.access.models.base import BaseModel

class UserDepartment(BaseModel):
    user = models.ForeignKey('access.User', on_delete=models.CASCADE)
    department = models.ForeignKey('users.Department', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} - {self.department}"

