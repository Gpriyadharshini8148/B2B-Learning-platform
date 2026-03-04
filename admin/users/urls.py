from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

# ── Flat/ViewSet-based views (kept for backward compat) ─────────────────────
from .views.profile_api import UserProfileAPIView
from .views.enrollment_api import StudentEnrollmentViewSet
from .views.notification_api import StudentNotificationViewSet
from .views.progress_api import StudentProgressAPIView
from .views.category_api import StudentCategoryViewSet
from .views.quiz_api import StudentQuizAttemptViewSet

# ── Fully nested views ───────────────────────────────────────────────────────
from .views.nested_course_api import (
    # courses
    NestedCourseListAPIView,
    NestedCourseDetailAPIView,
    # sections
    NestedSectionListAPIView,
    NestedSectionDetailAPIView,
    # lessons
    NestedLessonListAPIView,
    NestedLessonDetailAPIView,
    # lesson actions
    NestedLessonVideoAPIView,
    NestedMarkCompleteAPIView,
    NestedWatchTimeAPIView,
    # questions
    NestedQuestionListAPIView,
    NestedQuestionDetailAPIView,
    # options
    NestedOptionListAPIView,
    NestedOptionDetailAPIView,
)

# ── Router (non-nested endpoints) ───────────────────────────────────────────
router = DefaultRouter()
router.register('enrollments',   StudentEnrollmentViewSet,  basename='user-enrollments')
router.register('notifications', StudentNotificationViewSet, basename='user-notifications')
router.register('categories',    StudentCategoryViewSet,     basename='user-categories')
router.register('quiz-attempts', StudentQuizAttemptViewSet,  basename='user-quiz-attempts')


@api_view(['GET'])
def users_root(request):
    base = request.build_absolute_uri('/api/users/')
    return Response({
        'profile': {
            'me':      base + 'me/',
            'profile': base + 'profile/',
        },
        'learning': {
            'enrollments':   base + 'enrollments/',
            'courses':       base + 'courses/',
            'categories':    base + 'categories/',
            'progress':      base + 'progress/',
        },
        'nested_hierarchy': {
            'courses':       'courses/',
            'sections':      'courses/<course_id>/sections/',
            'lessons':       'courses/<course_id>/sections/<section_id>/lessons/',
            'video':         'courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/video/',
            'mark_complete': 'courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/mark-complete/',
            'watch_time':    'courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/watch-time/',
            'questions':     'courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/',
            'options':       'courses/<course_id>/sections/<section_id>/lessons/<lesson_id>/questions/<question_id>/options/',
        },
        'system': {
            'notifications': base + 'notifications/',
            'unread-count':  base + 'notifications/unread-count/',
        },
    })


# ── Base path for nested course URLs ────────────────────────────────────────
_C  = 'courses/'
_CS = 'courses/<int:course_id>/sections/'
_CSL = 'courses/<int:course_id>/sections/<int:section_id>/lessons/'
_CSLQ = (
    'courses/<int:course_id>/sections/<int:section_id>'
    '/lessons/<int:lesson_id>/questions/'
)
_CSLQO = (
    'courses/<int:course_id>/sections/<int:section_id>'
    '/lessons/<int:lesson_id>/questions/<int:question_id>/options/'
)

urlpatterns = [
    path('', users_root, name='users-root'),

    path('profile/', UserProfileAPIView.as_view(), name='user-profile'),
    path('me/',      UserProfileAPIView.as_view(), name='user-me'),

    path('progress/',                StudentProgressAPIView.as_view(), name='user-progress-root'),
    path('progress/<int:course_id>/', StudentProgressAPIView.as_view(), name='user-progress-detail'),

    path(_C,
         NestedCourseListAPIView.as_view(),
         name='user-course-list'),

    path('courses/<int:course_id>/',
         NestedCourseDetailAPIView.as_view(),
         name='user-course-detail'),

    # ── /courses/<id>/sections/ ────────────────────────────────────────────
    path(_CS,
         NestedSectionListAPIView.as_view(),
         name='user-section-list'),

    path(_CS + '<int:section_id>/',
         NestedSectionDetailAPIView.as_view(),
         name='user-section-detail'),

    # ── /courses/<id>/sections/<id>/lessons/ ───────────────────────────────
    path(_CSL,
         NestedLessonListAPIView.as_view(),
         name='user-lesson-list'),

    path(_CSL + '<int:lesson_id>/',
         NestedLessonDetailAPIView.as_view(),
         name='user-lesson-detail'),

    # ── lesson actions ─────────────────────────────────────────────────────
    path(_CSL + '<int:lesson_id>/video/',
         NestedLessonVideoAPIView.as_view(),
         name='user-lesson-video'),

    path(_CSL + '<int:lesson_id>/mark-complete/',
         NestedMarkCompleteAPIView.as_view(),
         name='user-lesson-mark-complete'),

    path(_CSL + '<int:lesson_id>/watch-time/',
         NestedWatchTimeAPIView.as_view(),
         name='user-lesson-watch-time'),

    # ── /courses/.../lessons/<id>/questions/ ───────────────────────────────
    path(_CSLQ,
         NestedQuestionListAPIView.as_view(),
         name='user-question-list'),

    path(_CSLQ + '<int:question_id>/',
         NestedQuestionDetailAPIView.as_view(),
         name='user-question-detail'),

    # ── /courses/.../questions/<id>/options/ ───────────────────────────────
    path(_CSLQO,
         NestedOptionListAPIView.as_view(),
         name='user-option-list'),

    path(_CSLQO + '<int:option_id>/',
         NestedOptionDetailAPIView.as_view(),
         name='user-option-detail'),

    # ── ViewSet routes (enrollments, notifications, categories, quiz attempts)
    path('', include(router.urls)),
]
