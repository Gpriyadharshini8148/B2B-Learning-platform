from django.db import models
from admin.access.models.base import BaseModel
from admin.organizations.models.organization import Organization

class Category(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='categories', null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
