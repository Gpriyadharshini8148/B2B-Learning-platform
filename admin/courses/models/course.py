from django.db import models
from admin.access.models.user import User
from .category import Category
from admin.access.models.base import BaseModel

class Course(BaseModel):
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='instructed_courses')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    title = models.CharField(max_length=255)
    description = models.TextField()
    level = models.CharField(max_length=100)
    language = models.CharField(max_length=100)

    thumbnail_url = models.URLField(blank=True, null=True)
    is_global = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
