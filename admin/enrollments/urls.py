from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.enrollment_views import EnrollmentViewSet

router = DefaultRouter()
router.register('list', EnrollmentViewSet, basename='enrollment')

@api_view(['GET'])
def enroll_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
    })

urlpatterns = [
    path('', enroll_root, name='enroll-root'),
    path('', include(router.urls)),
]
