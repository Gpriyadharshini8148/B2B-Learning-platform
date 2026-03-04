import logging
from rest_framework import views, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.http import HttpResponse
from django.conf import settings
from tablib import Dataset
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

# Models
from admin.organizations.models.organization import Organization
from admin.access.models import (
    UserNotification, User, Course, Enrollment, 
    Quiz, Subscription, Notification
)

logger = logging.getLogger(__name__)

# --- Resources ---

class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ('subdomain',)
        fields = ('id', 'name', 'subdomain', 'is_active', 'approval_status')

class UserResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    class Meta:
        model = User
        import_id_fields = ('email',)
        fields = ('id', 'first_name', 'last_name', 'email', 'organization', 'is_active', 'approval_status', 'is_verified')

class CourseResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    instructor = fields.Field(
        column_name='instructor_email',
        attribute='instructor',
        widget=ForeignKeyWidget(User, 'email')
    )
    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'organization', 'instructor', 'level', 'language', 'is_published', 'is_global')

class EnrollmentResource(resources.ModelResource):
    user = fields.Field(
        column_name='user_email',
        attribute='user',
        widget=ForeignKeyWidget(User, 'email')
    )
    course = fields.Field(
        column_name='course_title',
        attribute='course',
        widget=ForeignKeyWidget(Course, 'title') # Simplified, assumes unique titles or handles via email/context
    )
    class Meta:
        model = Enrollment
        fields = ('id', 'user', 'course', 'status')

class QuizResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    course = fields.Field(
        column_name='course_title',
        attribute='course',
        widget=ForeignKeyWidget(Course, 'title')
    )
    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'organization', 'course', 'passing_score')

class SubscriptionResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    class Meta:
        model = Subscription
        fields = ('id', 'organization', 'plan_name', 'end_date')

class NotificationResource(resources.ModelResource):
    organization = fields.Field(
        column_name='organization_subdomain',
        attribute='organization',
        widget=ForeignKeyWidget(Organization, 'subdomain')
    )
    class Meta:
        model = Notification
        fields = ('id', 'title', 'message', 'type', 'organization')

# --- Registry ---

# Mapping display names to registry keys (lowercase, no spaces/special chars)
MODEL_REGISTRY = {
    'organization': {'model': Organization, 'resource': OrganizationResource},
    'organizations': {'model': Organization, 'resource': OrganizationResource},
    'user': {'model': User, 'resource': UserResource},
    'users': {'model': User, 'resource': UserResource},
    'course': {'model': Course, 'resource': CourseResource},
    'access': {'model': Course, 'resource': CourseResource},
    'enrollment': {'model': Enrollment, 'resource': EnrollmentResource},
    'enrollments': {'model': Enrollment, 'resource': EnrollmentResource},
    'quiz': {'model': Quiz, 'resource': QuizResource},
    'quizzes': {'model': Quiz, 'resource': QuizResource},
    'subscription': {'model': Subscription, 'resource': SubscriptionResource},
    'subscriptions': {'model': Subscription, 'resource': SubscriptionResource},
    'notification': {'model': Notification, 'resource': NotificationResource},
    'notifications': {'model': Notification, 'resource': NotificationResource},
}

# --- Helper Functions ---

def get_allowed_queryset(user, model_name):
    if model_name not in MODEL_REGISTRY:
        return None
        
    config = MODEL_REGISTRY[model_name]
    model = config['model']
    base_qs = model.objects.all()
    
    # Super Admin Check
    super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

    if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
        return base_qs
        
    # Org Admin Check
    if hasattr(user, 'organization') and user.organization:
        org = user.organization
        if model == Organization:
            return base_qs.filter(id=org.id)
        elif model == User:
            return base_qs.filter(organization=org)
        elif model == Course:
            return base_qs.filter(organization=org)
        elif model == Enrollment:
            return base_qs.filter(course__organization=org)
        elif model == Quiz:
            return base_qs.filter(organization=org)
        elif model == Subscription:
            return base_qs.filter(organization=org)
        elif model == Notification:
            return base_qs.filter(organization=org)
            
    return base_qs.none()

def enforce_import_data_rules(user, model_name, dataset):
    super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')

    if user.is_superuser or getattr(user, 'email', '') == super_admin_email:
        return True, dataset, None
        
    if not (hasattr(user, 'organization') and user.organization):
        return False, dataset, "User has no associated organization."

    org = user.organization
    config = MODEL_REGISTRY[model_name]
    model = config['model']

    # Rule: Org Admin constraints
    if model == Organization:
        return False, dataset, "Only super admins can import Organizations."

    # Force company context for Org Admins
    if 'organization_subdomain' in dataset.headers:
        # Check if they are trying to import into another org
        indices = [dataset.headers.index('organization_subdomain')]
        for row in dataset:
            if row[indices[0]] != org.subdomain:
                 return False, dataset, f"You can only import data for your organization ({org.subdomain})."

    # If header missing, inject it
    if 'organization_subdomain' not in dataset.headers:
        dataset.append_col([org.subdomain] * len(dataset), header='organization_subdomain')

    return True, dataset, None

# --- API View ---

class GenericExportAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, model_name):
        # Normalizing model name (e.g. User -> users)
        lookup_name = model_name.lower().strip()
        
        if lookup_name not in MODEL_REGISTRY:
            return Response({
                "error": f"Model '{model_name}' not found or not registered for export.",
                "available_models": sorted(list(set(MODEL_REGISTRY.keys())))
            }, status=status.HTTP_404_NOT_FOUND)
            
        queryset = get_allowed_queryset(request.user, lookup_name)
        if queryset is None:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        resource_class = MODEL_REGISTRY[lookup_name]['resource']
        resource = resource_class()
        
        dataset = resource.export(queryset)
        export_format = request.query_params.get('format', 'csv').lower()
        
        filename = f"{lookup_name}_export"
        
        if export_format in ['xlsx', 'excel']:
            response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
        elif export_format == 'xls':
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="{filename}.xls"'
        elif export_format == 'json':
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        else:
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
            
        return response

class GenericImportAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request, model_name):
        lookup_name = model_name.lower().strip()
        if lookup_name not in MODEL_REGISTRY:
            return Response({
                "error": f"Model '{model_name}' not found or not registered for import.",
                "available_models": sorted(list(set(MODEL_REGISTRY.keys())))
            }, status=status.HTTP_404_NOT_FOUND)
            
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        dataset = Dataset()
        try:
            file_extension = file.name.split('.')[-1].lower() if '.' in file.name else 'csv'
            content = file.read()
            if file_extension in ['xlsx', 'xls']:
                dataset.load(content, format=file_extension)
            else:
                dataset.load(content.decode('utf-8-sig'), format='csv') # Handle BOM
        except Exception as e:
            logger.error(f"Failed to parse file: {e}")
            return Response({"error": f"Failed to parse file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
            
        is_allowed, dataset, error_msg = enforce_import_data_rules(request.user, lookup_name, dataset)
        if not is_allowed:
            return Response({"error": error_msg}, status=status.HTTP_403_FORBIDDEN)
            
        resource_class = MODEL_REGISTRY[lookup_name]['resource']
        resource = resource_class()
        
        # Dry run for validation
        result = resource.import_data(dataset, dry_run=True)
        
        if not result.has_errors():
            resource.import_data(dataset, dry_run=False)
            return Response({
                "message": f"Successfully imported {len(dataset)} {lookup_name} records.",
                "totals": result.totals
            })
        else:
            errors = []
            for row_error in result.row_errors():
                errors.append({"row": row_error[0], "errors": [str(e.error) for e in row_error[1]]})
            return Response({
                "error": "Import validation failed", 
                "details": errors
            }, status=status.HTTP_400_BAD_REQUEST)
