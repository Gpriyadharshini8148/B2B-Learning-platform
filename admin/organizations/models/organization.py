from django.db import models
from admin.access.models.base import BaseModel
import uuid

class Organization(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_otp', 'Pending OTP'),
    ]

    name = models.CharField(max_length=255)
    subdomain = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    # Overriding BaseModel field to keep organization inactive until approved
    is_active = models.BooleanField(default=False) 
    is_verified = models.BooleanField(default=False) 
    
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approval_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name