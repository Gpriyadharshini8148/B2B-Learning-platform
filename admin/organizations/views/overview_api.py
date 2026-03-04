from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from admin.access.permissions.tenant_permissions import IsOrganizationAdmin
from admin.access.models.user import User
from admin.access.models.course import Course
from admin.access.models.enrollment import Enrollment
from admin.organizations.models.invitation import Invitation

class OrgOverviewAPIView(APIView):
    """
    Provides a high-level summary of the organization's metrics.
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    def get(self, request):
        user = request.user
        
        # If accessing via Session (Django native User), fetch the corresponding Custom User profile
        if not hasattr(user, 'organization'):
            # Fallback: identify the user in our custom table by email
            user_profile = User.objects.filter(email=getattr(user, 'email', '')).first()
            if not user_profile:
                 return Response({"error": "Admin user profile not found."}, status=403)
            org = user_profile.organization
        else:
            org = user.organization

        if not org:
            return Response({"error": "No organization associated"}, status=400)

        total_learners = User.objects.filter(organization=org).count()
        active_courses = Course.objects.filter(organization_courses__organization=org, is_active=True).count()
        total_enrollments = Enrollment.objects.filter(user__organization=org).count()
        pending_invites = Invitation.objects.filter(organization=org, is_used=False).count()

        return Response({
            "organization_name": org.name,
            "stats": {
                "total_learners": total_learners,
                "active_courses": active_courses,
                "total_enrollments": total_enrollments,
                "pending_invitations": pending_invites
            }
        })
