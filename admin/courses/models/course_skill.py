from django.db import models
from .course import Course
from .skill import Skill
from admin.access.models.base import BaseModel

class CourseSkill(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='course_skills')

    def __str__(self):
        return f"{self.course.title} - {self.skill.name}"
