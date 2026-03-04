from django.db import models
from admin.access.models.base import BaseModel

class Skill(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='skills', null=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = 'courses_skill'

    def __str__(self):
        return self.name
