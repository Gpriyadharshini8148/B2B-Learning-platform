from rest_framework import viewsets, permissions
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin
from admin.access.models.course_assignment import CourseAssignment
from ..serializers.course_assignment_serializer import CourseAssignmentSerializer

class OrgAssignedLearningViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for Org Admins to assign courses to users and track those assignments.
    """
    serializer_class = CourseAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]
    queryset = CourseAssignment.objects.all()

    def get_queryset(self):
        # Filter assignments belonging to users in the admin's organization
        return CourseAssignment.objects.filter(user__organization=self.request.user.organization)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
