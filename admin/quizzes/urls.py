from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.quiz_views import QuizViewSet

router = DefaultRouter()
router.register('list', QuizViewSet, basename='quiz')

@api_view(['GET'])
def quiz_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
    })

urlpatterns = [
    path('', quiz_root, name='quiz-root'),
    path('', include(router.urls)),
]
