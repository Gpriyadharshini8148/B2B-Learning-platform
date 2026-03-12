from django.db import models
from .base import BaseModel
from .user import User
from .course import Course

class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        db_table = 'wishlist'
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.title}"
