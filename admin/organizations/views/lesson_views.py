from django.conf import settings
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from admin.access.models.lesson import Lesson
from ..serializers.lesson_serializer import LessonSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrgAdminOrReadOnly

class OrgLessonViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsOrgAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            queryset = Lesson.objects.all()
        else:
            queryset = Lesson.objects.filter(organization=user.organization)

        # Handle nested filtering
        course_pk = self.kwargs.get('course_pk')
        section_pk = self.kwargs.get('section_pk')
        if section_pk:
            queryset = queryset.filter(section_id=section_pk)
        elif course_pk:
            queryset = queryset.filter(section__course_id=course_pk)
            
        return queryset

    def perform_create(self, serializer):
        course_pk = self.kwargs.get('course_pk')
        section_pk = self.kwargs.get('section_pk')
        order_number = serializer.validated_data.get('order_number')
        
        # Determine section_id
        if section_pk:
            section_id = section_pk
        else:
            section = serializer.validated_data.get('section')
            if not section:
                # If we are in a nested context but no section provided in body, it's an error unless section_pk is in URL
                if not section_pk:
                     raise ValidationError("Section is required")
                section_id = section_pk
            else:
                section_id = section.id
            
        # Replace logic: Check if a lesson with this order_number exists in this section
        existing_lesson = Lesson.objects.filter(
            section_id=section_id, 
            order_number=order_number
        ).first()

        if existing_lesson:
            serializer.instance = existing_lesson
            
        serializer.save(
            organization=self.request.user.organization,
            section_id=section_id
        )
