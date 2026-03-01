from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.enrollment_views import EnrollmentViewSet
from .views.progress_views import ProgressViewSet, LessonProgressViewSet
from .views.certificate_views import CertificateViewSet

router = DefaultRouter()
router.register('list', EnrollmentViewSet, basename='enrollment')
router.register('course-progress', ProgressViewSet, basename='course-progress')
router.register('lesson-progress', LessonProgressViewSet, basename='lesson-progress')
router.register('certificates', CertificateViewSet, basename='certificate')

@api_view(['GET'])
def enroll_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
        'course-progress': request.build_absolute_uri('course-progress/'),
        'lesson-progress': request.build_absolute_uri('lesson-progress/'),
        'certificates': request.build_absolute_uri('certificates/'),
    })

urlpatterns = [
    path('', enroll_root, name='enroll-root'),
    path('', include(router.urls)),
]
