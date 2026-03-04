from django.db import models
from admin.access.models.base import BaseModel

class Subscription(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='subscriptions')
    plan_name = models.CharField(max_length=255)
    end_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscriptions_subscription'

    def __str__(self):
        return f"Plan: {self.plan_name}"
