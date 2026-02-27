from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.department_views import DepartmentViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')

@api_view(['GET'])
def users_root(request):
    return Response({
        'departments': request.build_absolute_uri('departments/'),
    })

urlpatterns = [
    path('', users_root, name='users-root'),
    path('', include(router.urls)),
]
