from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views.course_views import CourseViewSet
from .views.category_views import CategoryViewSet
from .views.section_views import SectionViewSet
from .views.lesson_views import LessonViewSet
from .views.skill_views import SkillViewSet
from .views.learning_path_views import LearningPathViewSet

router = DefaultRouter()
router.register('list', CourseViewSet, basename='course')
router.register('categories', CategoryViewSet, basename='category')
router.register('sections', SectionViewSet, basename='section')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('skills', SkillViewSet, basename='skill')
router.register('learning-paths', LearningPathViewSet, basename='learning-path')

@api_view(['GET'])
def courses_root(request):
    return Response({
        'list': request.build_absolute_uri('list/'),
        'categories': request.build_absolute_uri('categories/'),
        'sections': request.build_absolute_uri('sections/'),
        'lessons': request.build_absolute_uri('lessons/'),
        'skills': request.build_absolute_uri('skills/'),
        'learning-paths': request.build_absolute_uri('learning-paths/'),
    })

urlpatterns = [
    path('', courses_root, name='courses-root'),
    path('', include(router.urls)),
]
