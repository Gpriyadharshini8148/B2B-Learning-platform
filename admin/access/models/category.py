from django.db import models
from admin.access.models.base import BaseModel

class Category(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='categories', null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'courses_category'

    def __str__(self):
        return self.name
