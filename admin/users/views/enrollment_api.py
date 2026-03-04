from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from admin.access.models.enrollment import Enrollment
from ..serializers.user_enrollment_serializer import StudentEnrollmentSerializer
from django.db.models import Q

class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    GET /api/user/enrollments (filter: all, completed, in-progress, archived)
    GET /api/user/enrollments/search?q=
    GET /api/user/enrollments/{id}
    PUT /api/user/enrollments/{id}/archive
    """
    serializer_class = StudentEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Enrollment.objects.filter(user=user)
        
        # Filtering logic
        status_filter = self.request.query_params.get('filter')
        if status_filter == 'completed':
            queryset = queryset.filter(status='completed')
        elif status_filter == 'in-progress':
            queryset = queryset.filter(status='active')
        elif status_filter == 'archived':
            queryset = queryset.filter(status='archived')
            
        # Search logic
        search_query = self.request.query_params.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(course__title__icontains=search_query) | 
                Q(course__description__icontains=search_query)
            )
            
        return queryset

    @action(detail=True, methods=['put'])
    def archive(self, request, pk=None):
        enrollment = self.get_object()
        enrollment.status = 'archived'
        enrollment.save()
        return Response({"message": "Course archived successfully", "status": "archived"})
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        return self.list(request)

    def perform_create(self, serializer):
        user = self.request.user
        course = serializer.validated_data.get('course')
        
        if Enrollment.objects.filter(user=user, course=course).exists():
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"message": "You are already enrolled in this course."})
            
        serializer.save(user=user)
