from rest_framework import views, permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from admin.access.models import Enrollment, CourseProgress

class StudentProgressSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    progress_percentage = serializers.FloatField()
    completed_at = serializers.DateTimeField(allow_null=True)

class StudentProgressAPIView(views.APIView):
    """
    GET /api/user/progress/{course_id}
    POST /api/user/progress
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: StudentProgressSerializer(many=True), 404: dict},
        operation_id="api_users_progress_list_or_retrieve" 
    )
    def get(self, request, course_id=None):

        user = request.user
        
        if course_id:
            try:
                enrollment = Enrollment.objects.get(user=user, course_id=course_id)
                progress, created = CourseProgress.objects.get_or_create(enrollment=enrollment)
                return Response({
                    "course_id": course_id,
                    "course_title": enrollment.course.title,
                    "progress_percentage": progress.progress_percentage,
                    "completed_at": progress.completed_at
                })
            except Enrollment.DoesNotExist:
                return Response({"error": "Not enrolled in this course"}, status=status.HTTP_404_NOT_FOUND)
        
        # List all progress
        enrollments = Enrollment.objects.filter(user=user)
        results = []
        for enrollment in enrollments:
            progress, _ = CourseProgress.objects.get_or_create(enrollment=enrollment)
            results.append({
                "course_id": enrollment.course.id,
                "course_title": enrollment.course.title,
                "progress_percentage": progress.progress_percentage,
                "completed_at": progress.completed_at
            })
        return Response(results)

    @extend_schema(
        request={'course_id': int, 'progress_percentage': float}, 
        responses={200: dict, 400: dict, 404: dict},
        operation_id="api_users_progress_create_or_update"
    )
    def post(self, request, course_id=None):
        course_id = request.data.get('course_id')
        progress_val = request.data.get('progress_percentage')
        
        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            enrollment = Enrollment.objects.get(user=request.user, course_id=course_id)
            progress, created = CourseProgress.objects.get_or_create(enrollment=enrollment)
            if progress_val is not None:
                progress.progress_percentage = progress_val
                progress.save()
            return Response({
                "message": "Progress updated successfully",
                "progress_percentage": progress.progress_percentage
            })
        except Enrollment.DoesNotExist:
            return Response({"error": "Not enrolled in this course"}, status=status.HTTP_404_NOT_FOUND)
