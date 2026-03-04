import json
import logging
from django.utils.deprecation import MiddlewareMixin
from admin.access.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log all modifications (POST, PUT, PATCH, DELETE)
    made to the application via generic API calls.
    Logs who made the request, the action type, entity info, and response status.
    """
    
    def process_response(self, request, response):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = getattr(request, 'user', None)
            
            # Ensure the user is authenticated 
            if user and user.is_authenticated:
                
                # SuperAdmins might not have organizations explicitly set
                org = getattr(user, 'organization', None)
                
                # Basic Entity ID extraction from URL paths
                path_parts = [p for p in request.path.split('/') if p]
                entity_id = 0
                for part in reversed(path_parts):
                    if part.isdigit():
                        entity_id = int(part)
                        break
                        
                # Determine entity type from URL
                entity_type = "API Request"
                if len(path_parts) >= 2:
                    # Generic heuristic (e.g., api/users/ -> Users)
                    base_resource = path_parts[-2] if path_parts[-1].isdigit() else path_parts[-1]
                    entity_type = base_resource.capitalize().replace('-', ' ')

                metadata = {
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                }

                try:
                    AuditLog.objects.create(
                        organization=org,
                        user=user,
                        action=request.method,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        metadata=json.dumps(metadata)
                    )
                except Exception as e:
                    logger.error(f"Failed to create audit log for {user} on {request.path}: {e}")

        return response
