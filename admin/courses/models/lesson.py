from django.db import models
from .section import Section
from admin.access.models.base import BaseModel

class Lesson(BaseModel):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    video_url = models.URLField(blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)
    order_number = models.IntegerField()
    is_preview = models.BooleanField(default=False)

    def __str__(self):
        return self.title
