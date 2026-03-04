from django.db import models
from .section import Section
from .video import Video
from admin.access.models.base import BaseModel

class Lesson(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='lessons', null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    title = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(default=0)

    order_number = models.IntegerField()
    is_preview = models.BooleanField(default=False)

    class Meta:
        db_table = 'courses_lesson'

    def __str__(self):
        return self.title
