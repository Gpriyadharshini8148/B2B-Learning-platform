from django.db import models
from .organization import Organization
from admin.access.models.base import BaseModel

class OrganizationDomain(BaseModel):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="domains"
    )
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.domain