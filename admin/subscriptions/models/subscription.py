from django.db import models
from admin.organizations.models.organization import Organization
from admin.access.models.base import BaseModel

class Subscription(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=255)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.organization.name} - {self.plan_name}"
