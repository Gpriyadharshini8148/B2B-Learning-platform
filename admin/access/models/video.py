from django.db import models
from admin.access.models.base import BaseModel

class Video(BaseModel):
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='videos', null=True)
    title = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='videos/')
    duration_seconds = models.IntegerField(default=0)

    class Meta:
        db_table = 'courses_video'

    def __str__(self):
        return self.title
