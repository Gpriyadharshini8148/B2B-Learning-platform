import logging
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from tablib import Dataset
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Models
from admin.organizations.models.organization import Organization
from admin.access.models.user import User
from admin.courses.models.course import Course
from admin.enrollments.models.enrollment import Enrollment
from admin.quizzes.models.quiz import Quiz
from admin.subscriptions.models.subscription import Subscription
from admin.notifications.models.notification import Notification

logger = logging.getLogger(__name__)

# --- Resources ---

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ('subdomain',)
        fields = ('name', 'subdomain', 'industry', 'is_active', 'approval_status')

class UserResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    class Meta:
        model = User
        import_id_fields = ('email',)
        fields = ('first_name', 'last_name', 'email', 'organization', 'is_active', 'approval_status')

class CourseResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    class Meta:
        model = Course
        fields = ('title', 'description', 'organization', 'is_published')

class EnrollmentResource(resources.ModelResource):
    class Meta:
        model = Enrollment
        fields = ('user', 'course', 'enrolled_at')

class QuizResource(resources.ModelResource):
    class Meta:
        model = Quiz
        fields = ('title', 'course', 'passing_score')

class SubscriptionResource(resources.ModelResource):
    class Meta:
        model = Subscription
        fields = ('user', 'plan_name', 'start_date', 'end_date')

class NotificationResource(resources.ModelResource):
    class Meta:
        model = Notification
        fields = ('title', 'message', 'recipient_type')

# --- Registry ---

MODEL_REGISTRY = {
    'organizations': {'model': Organization, 'resource': OrganizationResource},
    'users': {'model': User, 'resource': UserResource},
    'courses': {'model': Course, 'resource': CourseResource},
    'enrollments': {'model': Enrollment, 'resource': EnrollmentResource},
    'quizzes': {'model': Quiz, 'resource': QuizResource},
    'subscriptions': {'model': Subscription, 'resource': SubscriptionResource},
    'notifications': {'model': Notification, 'resource': NotificationResource},
}

# --- Helper Functions ---

def get_allowed_queryset(user, model_name):
    if model_name not in MODEL_REGISTRY:
        return None
        
    config = MODEL_REGISTRY[model_name]
    model = config['model']
    base_qs = model.objects.all()
    
    # Super Admin can see EVERYTHING
    from django.conf import settings
    super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

    if user.is_superuser or getattr(user, 'role', None) == 'SUPERADMIN' or getattr(user, 'email', '') == super_admin_email:
        return base_qs
        
    # Org Admin can only see their organization's data
    if hasattr(user, 'organization') and user.organization:
        org = user.organization
        if model == Organization:
            return base_qs.filter(id=org.id)
        elif model == User:
            return base_qs.filter(organization=org)
        elif model == Course:
            return base_qs.filter(organization_courses__organization=org)
        elif model == Enrollment:
            return base_qs.filter(course__organization_courses__organization=org)
        elif model == Quiz:
            return base_qs.filter(course__organization_courses__organization=org)
        elif model == Subscription:
            return base_qs.filter(organization=org)
        # Notifications don't have an organization field, so they're either empty or global. We return none for org admins.
        return base_qs.none()
        
    return base_qs.none()

def enforce_import_data_rules(user, model_name, dataset):
    from django.conf import settings
    super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

    if user.is_superuser or getattr(user, 'role', None) == 'SUPERADMIN' or getattr(user, 'email', '') == super_admin_email:
        return True, dataset, None
        
    if not (hasattr(user, 'organization') and user.organization):
        return False, dataset, "User has no associated organization."

    org = user.organization
    config = MODEL_REGISTRY[model_name]
    model = config['model']

    # Rule: Org Admin can only import data for THEIR organization
    if model == Organization:
        return False, dataset, "Only super admins can import Organizations."

    if model == User:
        if 'organization_subdomain' in dataset.headers:
            del dataset['organization_subdomain']
        dataset.append_col([org.subdomain] * len(dataset), header='organization_subdomain')
        return True, dataset, None
        
    if model == Subscription:
        if 'organization' in dataset.headers:
            del dataset['organization']
        dataset.append_col([org.id] * len(dataset), header='organization')
        return True, dataset, None
        
    if model == Notification:
        return False, dataset, "Only super admins can import Notifications."

    if model in [Course, Enrollment, Quiz]:
        return True, dataset, None

    return False, dataset, "Permission denied for importing."

# --- API View ---

class GenericExportAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, model_name):
        model_name = model_name.lower().replace('-', '')
        if model_name not in MODEL_REGISTRY:
            return Response({"error": "Model not found or not registered for export."}, status=status.HTTP_404_NOT_FOUND)
            
        queryset = get_allowed_queryset(request.user, model_name)
        if queryset is None:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        resource_class = MODEL_REGISTRY[model_name]['resource']
        resource = resource_class()
        
        dataset = resource.export(queryset)
        export_format = request.query_params.get('format', 'csv').lower()
        
        if export_format in ['xlsx', 'excel']:
            response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{model_name}.xlsx"'
        elif export_format == 'xls':
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{model_name}.xls"'
        else:
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{model_name}.csv"'
            
        return response

class GenericImportAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request, model_name):
        model_name = model_name.lower().replace('-', '')
        if model_name not in MODEL_REGISTRY:
            return Response({"error": "Model not found or not registered for import."}, status=status.HTTP_404_NOT_FOUND)
            
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        dataset = Dataset()
        try:
            file_extension = file.name.split('.')[-1].lower() if '.' in file.name else 'csv'
            if file_extension in ['xlsx', 'xls']:
                dataset.load(file.read(), format=file_extension)
            else:
                dataset.load(file.read().decode('utf-8'), format='csv')
        except Exception as e:
            logger.error(f"Failed to parse file: {e}")
            return Response({"error": f"Failed to parse file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
        is_allowed, dataset, error_msg = enforce_import_data_rules(request.user, model_name, dataset)
        if not is_allowed:
            return Response({"error": error_msg}, status=status.HTTP_403_FORBIDDEN)
            
        resource_class = MODEL_REGISTRY[model_name]['resource']
        resource = resource_class()
        
        # Dry run for validation
        result = resource.import_data(dataset, dry_run=True)
        
        if not result.has_errors():
            resource.import_data(dataset, dry_run=False)
            return Response({
                "message": f"Successfully imported {len(dataset)} {model_name} records.",
                "created": result.totals['new'],
                "updated": result.totals['update']
            })
        else:
            errors = []
            for row_error in result.row_errors():
                errors.append(f"Row {row_error[0]}: {str(row_error[1][0].error)}")
            return Response({"error": "Import failed", "details": errors}, status=status.HTTP_400_BAD_REQUEST)
