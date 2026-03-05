from django.db import models
from .base import BaseModel

class Role(BaseModel):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('organization_admin', 'Organization Admin'),
        ('organization_user', 'Organization User'),
    ]

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name="roles",
        null=True,  # Super admins might not belong to a specific org
        blank=True
    )

    name = models.CharField(max_length=50, choices=ROLE_CHOICES)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()
