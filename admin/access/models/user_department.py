from django.db import models
from admin.access.models.base import BaseModel

class UserDepartment(BaseModel):
    user = models.ForeignKey('access.User', on_delete=models.CASCADE)
    department = models.ForeignKey('access.Department', on_delete=models.CASCADE)

    class Meta:
        db_table = 'users_userdepartment'

    def __str__(self):
        return f"{self.user} - {self.department}"
