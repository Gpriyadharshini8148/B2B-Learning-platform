from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.quiz_views import QuizViewSet
from .views.question_views import QuestionViewSet
from .views.option_views import OptionViewSet

router = DefaultRouter()
router.register('list', QuizViewSet, basename='quiz')
router.register('questions', QuestionViewSet, basename='question')
router.register('options', OptionViewSet, basename='option')

@api_view(['GET'])
def quiz_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
        'questions': request.build_absolute_uri('questions/'),
        'options': request.build_absolute_uri('options/'),
    })

urlpatterns = [
    path('', quiz_root, name='quiz-root'),
    path('', include(router.urls)),
]
