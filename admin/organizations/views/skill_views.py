from django.conf import settings
from rest_framework import viewsets
from admin.access.models.skill import Skill
from ..serializers.skill_serializer import SkillSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class OrgSkillViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [IsOrgAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Skill.objects.all()
            
        return Skill.objects.filter(
            organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        serializer.save(
            organization=self.request.user.organization
        )
