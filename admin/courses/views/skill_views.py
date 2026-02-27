from rest_framework import viewsets
from ..models.skill import Skill
from ..serializers.skill_serializer import SkillSerializer

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
