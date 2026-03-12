import json
import logging
import threading
from django.utils.deprecation import MiddlewareMixin
from admin.access.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

def save_audit_log_task(org, user, method, entity_type, entity_id, metadata_json):
    """Background task to save audit logs to the database."""
    try:
        AuditLog.objects.create(
            organization=org,
            user=user,
            action=method,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata_json
        )
    except Exception as e:
        logger.error(f"Background audit log failed: {e}")

class AuditLogMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log all modifications (POST, PUT, PATCH, DELETE)
    made to the application via generic API calls.
    Logs who made the request, the action type, entity info, and response status.
    """
    
    def process_response(self, request, response):
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            user = getattr(request, 'user', None)
            
            # If user is anonymous or not authenticated, allow logging but set user to None
            if not user or not user.is_authenticated:
                user = None
            
            # Only set org if there's an authenticated user
            org = getattr(user, 'organization', None) if user else None
            
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

            # Run the database save in a background thread to avoid blocking the main request
            threading.Thread(
                target=save_audit_log_task,
                args=(org, user, request.method, entity_type, entity_id, json.dumps(metadata)),
                daemon=True
            ).start()

        return response
