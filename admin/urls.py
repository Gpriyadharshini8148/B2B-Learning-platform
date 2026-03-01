from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .import_export_api import GenericImportAPIView, GenericExportAPIView
from admin.access.views.approval_views import OrgApprovalView, UserApprovalView

@api_view(['GET'])
def admin_api_root(request, format=None):
    """
    Main entry point for the Udemy Clone Admin API.
    """
    return Response({
        'organizations-cms': reverse('org-root', request=request, format=format),
        'users-cms': reverse('users-root', request=request, format=format),
        'access-cms': reverse('access-root', request=request, format=format),
        'courses-cms': reverse('courses-root', request=request, format=format),
        'enrollments-cms': reverse('enroll-root', request=request, format=format),
        'quizzes-cms': reverse('quiz-root', request=request, format=format),
        'subscriptions-cms': reverse('sub-root', request=request, format=format),
        'notifications-cms': reverse('notif-root', request=request, format=format),
        'bulk-import': '/api/admin/bulk-cms/import/{model_name}/',
        'bulk-export': '/api/admin/bulk-cms/export/{model_name}/',
        'swagger-docs': reverse('swagger-ui', request=request, format=format),
        'redoc': reverse('redoc', request=request, format=format),
    })

urlpatterns = [
    path('', admin_api_root, name='admin-api-root'),
    path('bulk-cms/approve/org/<uuid:token>/<str:action>/', OrgApprovalView.as_view(), name='org-approve'),
    path('bulk-cms/approve/user/<uuid:token>/<str:action>/', UserApprovalView.as_view(), name='user-approve'),
    path('organizations/', include('admin.organizations.urls')),
    path('users/', include('admin.users.urls')),
    path('access/', include('admin.access.urls')),
    path('courses/', include('admin.courses.urls')),
    path('enrollments/', include('admin.enrollments.urls')),
    path('quizzes/', include('admin.quizzes.urls')),
    path('subscriptions/', include('admin.subscriptions.urls')),
    path('notifications/', include('admin.notifications.urls')),
    path('super_admin/', include('admin.super_admin_urls')),
    
    # Bulk Data Management
    path('bulk-cms/', include([
        path('import/<str:model_name>/', GenericImportAPIView.as_view(), name='bulk-import'),
        path('export/<str:model_name>/', GenericExportAPIView.as_view(), name='bulk-export'),
        path('import-export/', GenericImportAPIView.as_view(), name='bulk-import-export'), # legacy/fallback
    ])),
]
