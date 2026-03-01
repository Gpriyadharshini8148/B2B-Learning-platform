from django.db import models
from .subscription import Subscription
from admin.access.models.base import BaseModel
from admin.organizations.models.organization import Organization

class Payment(BaseModel):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='payments', null=True)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Payment {self.id} - {self.subscription.plan_name}"
