from django.db import models
from admin.access.models.base import BaseModel

class Notification(BaseModel):
    NOTIFICATION_TYPES = [
        ('system', 'System'),
        ('course', 'Course'),
        ('assignment', 'Assignment'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='system')

    def __str__(self):
        return self.title
