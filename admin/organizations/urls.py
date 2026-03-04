from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import (
    OrgOverviewAPIView, OrgManageUserViewSet, OrgInsightsAPIView,
    OrgAssignedLearningViewSet, OrgReviewPendingInvitesViewSet,
    OrgInviteNewUserView, OrgReviewLearnersViewSet, OrgUserActivityViewSet,
    OrgCheckProgressOfLearningViewSet,
    OrgCourseViewSet, OrgSectionViewSet, OrgLessonViewSet, 
    OrgVideoViewSet, OrgCategoryViewSet, OrgSkillViewSet, OrgLearningPathViewSet,
    OrgQuizViewSet, OrgQuestionViewSet, OrgOptionViewSet,
    OrgEnrollmentViewSet, OrgCourseProgressViewSet, 
    OrgLessonProgressViewSet, OrgCertificateViewSet,
    OrganizationViewSet, DomainViewSet, SSOViewSet, 
    AcceptInvitationView, OrgNotificationViewSet,
    OrgSubscriptionViewSet, OrgPaymentViewSet,
    OrgDepartmentViewSet, OrgUserDepartmentViewSet
)



router = DefaultRouter()
router.register('profile', OrganizationViewSet, basename='organization')
router.register('domains', DomainViewSet, basename='domain')
router.register('sso', SSOViewSet, basename='sso')
router.register('departments', OrgDepartmentViewSet, basename='org-departments')
router.register('user-departments', OrgUserDepartmentViewSet, basename='org-user-departments')

# Dashboard & Specialized Management
router.register('manage-users', OrgManageUserViewSet, basename='org-manage-users')
router.register('assigned-learning', OrgAssignedLearningViewSet, basename='org-assigned-learning')
router.register('pending-invites', OrgReviewPendingInvitesViewSet, basename='org-pending-invites')
router.register('learners-directory', OrgReviewLearnersViewSet, basename='org-learners')
router.register('activity-log', OrgUserActivityViewSet, basename='org-activity')
router.register('learning-paths-explore', OrgLearningPathViewSet, basename='org-lp-explore')
router.register('progress-audits', OrgCheckProgressOfLearningViewSet, basename='org-progress-audits')

# Content Management
router.register('courses', OrgCourseViewSet, basename='org-courses')
router.register('categories', OrgCategoryViewSet, basename='org-categories')
router.register('skills', OrgSkillViewSet, basename='org-skills')
router.register('learning-paths', OrgLearningPathViewSet, basename='org-learning-paths')

# Student Tracking
router.register('enrollments', OrgEnrollmentViewSet, basename='org-enrollments')
router.register('course-progress', OrgCourseProgressViewSet, basename='org-course-progress')
router.register('lesson-progress', OrgLessonProgressViewSet, basename='org-lesson-progress')
router.register('certificates', OrgCertificateViewSet, basename='org-certificates')
router.register('notifications', OrgNotificationViewSet, basename='org-notifications')
router.register('subscriptions', OrgSubscriptionViewSet, basename='org-subscriptions')
router.register('payments', OrgPaymentViewSet, basename='org-payments')

from drf_spectacular.utils import extend_schema

@extend_schema(responses={200: dict})
@api_view(['GET'])
def org_root(request):
    return Response({
        'overview': request.build_absolute_uri('overview/'),
        'insights': request.build_absolute_uri('insights/'),
        'profile': request.build_absolute_uri('profile/'),
        'management': {
            'users': {
                'directory': request.build_absolute_uri('learners-directory/'),
                'manage': request.build_absolute_uri('manage-users/'),
                'invite': request.build_absolute_uri('invite-v2/'),
                'pending-invites': request.build_absolute_uri('pending-invites/'),
                'activity': request.build_absolute_uri('activity-log/'),
            },
            'content': {
                'access': request.build_absolute_uri('courses/'),
                'categories': request.build_absolute_uri('categories/'),
                'skills': request.build_absolute_uri('skills/'),
                'learning-paths': request.build_absolute_uri('learning-paths/'),
                'learning-paths-explore': request.build_absolute_uri('learning-paths-explore/'),
            },
            'learning': {
                'assignments': request.build_absolute_uri('assigned-learning/'),
                'progress-audits': request.build_absolute_uri('progress-audits/'),
                'enrollments': request.build_absolute_uri('enrollments/'),
                'certificates': request.build_absolute_uri('certificates/'),
                'domains':request.build_absolute_uri('domains/'),
                'departments': request.build_absolute_uri('departments/'),
                'user-departments': request.build_absolute_uri('user-departments/'),
            },
            'billing': {
                'subscriptions': request.build_absolute_uri('subscriptions/'),
                'payments': request.build_absolute_uri('payments/'),
            },
            'alerts': {
                'notifications': request.build_absolute_uri('notifications/'),
            }
        }
    })

from django.urls import path, include

# Define nested URL patterns manually
nested_patterns = [
    # Video Management
    path('course/videos/', OrgVideoViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-course-videos'),
    path('course/videos/<int:pk>/', OrgVideoViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-course-videos-detail'),

    # Course -> Section Root
    path('course/<int:course_pk>/section/', OrgSectionViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-section-nested'),
    path('course/<int:course_pk>/section/<int:pk>/', OrgSectionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-section-nested-detail'),

    # Course -> Section -> Lesson Root
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/', OrgLessonViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-lesson-nested'),
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:pk>/', OrgLessonViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-lesson-nested-detail'),
    
    # Course -> Section -> Lesson -> Quiz
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/', OrgQuizViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-quiz-nested'),
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/<int:pk>/', OrgQuizViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-quiz-nested-detail'),
    
    # Course -> Section -> Lesson -> Quiz -> Questions
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/<int:quiz_pk>/questions/', OrgQuestionViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-questions-nested'),
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/<int:quiz_pk>/questions/<int:pk>/', OrgQuestionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-questions-nested-detail'),
    
    # Course -> Section -> Lesson -> Quiz -> Questions -> Options
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/<int:quiz_pk>/questions/<int:question_pk>/options/', OrgOptionViewSet.as_view({'get': 'list', 'post': 'create'}), name='org-options-nested'),
    path('course/<int:course_pk>/section/<int:section_pk>/lesson/<int:lesson_pk>/quiz/<int:quiz_pk>/questions/<int:question_pk>/options/<int:pk>/', OrgOptionViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='org-options-nested-detail'),
]

urlpatterns = [
    path('', org_root, name='org-root'),
    path('overview/', OrgOverviewAPIView.as_view(), name='org-overview'),
    path('insights/', OrgInsightsAPIView.as_view(), name='org-insights'),
    path('invite-v2/', OrgInviteNewUserView.as_view(), name='org-invite-v2'),
    
    # Standard flat routes (via router)
    path('', include(router.urls)),
    
    # Nested routes
    path('', include(nested_patterns)),

    path('invite/', OrgInviteNewUserView.as_view(), name='invite-user'),
    path('accept-invite/', AcceptInvitationView.as_view(), name='accept-invite'),
]


