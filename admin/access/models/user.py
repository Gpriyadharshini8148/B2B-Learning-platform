from django.db import models
from .base import BaseModel
import uuid

class User(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending_otp', 'Pending OTP'),
    ]

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()

    # Overriding BaseModel field to keep user inactive until approved
    is_active = models.BooleanField(default=False) 
    is_logged_in = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    
    approval_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approval_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    last_login = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.email

    @property
    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates or by permissions policies.
        """
        return True
