from django.db import models
from admin.access.models.base import BaseModel

class Department(BaseModel):
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name="departments"
    )

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
