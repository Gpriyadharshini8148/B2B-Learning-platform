from django.conf import settings
from rest_framework import viewsets
from admin.access.models.section import Section
from ..serializers.section_serializer import SectionSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class OrgSectionViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [IsOrgAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', '')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            queryset = Section.objects.all()
        else:
            queryset = Section.objects.filter(organization=user.organization)

        # Handle nested course filtering
        course_pk = self.kwargs.get('course_pk')
        if course_pk:
            queryset = queryset.filter(course_id=course_pk)
        return queryset

    def perform_create(self, serializer):
        course_pk = self.kwargs.get('course_pk')
        order_number = serializer.validated_data.get('order_number')
        
        # Logic from OrgSectionViewSet: replace if order_number exists
        if course_pk:
            existing_section = Section.objects.filter(
                course_id=course_pk, 
                order_number=order_number
            ).first()

            if existing_section:
                serializer.instance = existing_section
            
            serializer.save(
                organization=self.request.user.organization,
                course_id=course_pk
            )
        else:
            serializer.save(
                organization=self.request.user.organization
            )
