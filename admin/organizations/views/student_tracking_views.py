from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from admin.access.models import Enrollment, CourseProgress, LessonProgress, Certificate
from ..serializers.enrollment_serializer import EnrollmentSerializer
from ..serializers.course_progress_serializer import CourseProgressSerializer
from ..serializers.lesson_progress_serializer import LessonProgressSerializer
from ..serializers.certificate_serializer import CertificateSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin

class OrgEnrollmentViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific enrollment management.
    Allows Org Admins to see and manage all enrollments in their organization.
    """
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsOrganizationAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                "message": "Successfully enrolled",
                "data": serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(organization=user.organization)


class OrgCourseProgressViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific course progress management.
    Org Admins see everyone in their organization.
    """
    serializer_class = CourseProgressSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return CourseProgress.objects.all()
            
        return CourseProgress.objects.filter(
            enrollment__user__organization=user.organization
        )


class OrgLessonProgressViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific lesson progress management.
    Org Admins see everyone in their organization.
    """
    serializer_class = LessonProgressSerializer
    permission_classes = [IsOrganizationAdmin]
    
    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return LessonProgress.objects.all()

        return LessonProgress.objects.filter(
            enrollment__user__organization=user.organization
        )


class OrgCertificateViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization-specific certificate management.
    Org Admins see everyone in their organization.
    """
    serializer_class = CertificateSerializer
    permission_classes = [IsOrganizationAdmin]

    def get_queryset(self):
        user = self.request.user
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
            return Certificate.objects.filter(enrollment__status='completed')
            
        return Certificate.objects.filter(
            enrollment__user__organization=user.organization,
            enrollment__status='completed'
        )
