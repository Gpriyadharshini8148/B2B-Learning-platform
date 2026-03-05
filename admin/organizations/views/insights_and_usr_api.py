from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Avg, Count
from admin.access.permissions.tenant_permissions import IsOrganizationAdmin
from admin.access.models.course_progress import CourseProgress

from drf_spectacular.utils import extend_schema
from ..serializers.dashboard_serializers import OrgInsightsResponseSerializer

class OrgInsightsAPIView(APIView):
    """
    Provides analytics on organization-wide learning progress and popular courses.
    """
    permission_classes = [permissions.IsAuthenticated, IsOrganizationAdmin]

    @extend_schema(responses={200: OrgInsightsResponseSerializer})
    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({"error": "No organization associated"}, status=400)
            
        # Average completion percentage across all enrollments in the org
        avg_completion = CourseProgress.objects.filter(
            enrollment__user__organization=org
        ).aggregate(Avg('progress_percentage'))['progress_percentage__avg'] or 0

        # Most popular courses based on enrollment count
        popular_courses = CourseProgress.objects.filter(
            enrollment__user__organization=org
        ).values('enrollment__course__title').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        return Response({
            "average_org_completion": round(avg_completion, 2),
            "popular_courses": popular_courses
        })
