from django.db import models
from .base import BaseModel

class AuditLog(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE)
    user = models.ForeignKey('access.User', on_delete=models.SET_NULL, null=True)

    action = models.CharField(max_length=255)

    entity_type = models.CharField(max_length=255)
    entity_id = models.IntegerField()

    metadata = models.TextField(blank=True, null=True)


