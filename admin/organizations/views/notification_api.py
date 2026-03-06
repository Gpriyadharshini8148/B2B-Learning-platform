from django.conf import settings
from rest_framework import viewsets, permissions
from admin.access.models import Notification, UserNotification
from admin.organizations.serializers.notification_serializer import NotificationSerializer
from admin.access.permissions.tenant_permissions import TenantSafeViewSetMixin, IsOrganizationAdmin, IsSuperAdmin
from admin.access.models.user import User
from admin.organizations.models.organization import Organization

class OrgNotificationViewSet(TenantSafeViewSetMixin, viewsets.ModelViewSet):
    """
    Organization Admins view: Create and manage notifications for their OWN organization.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsOrganizationAdmin]
    queryset = Notification.objects.none()

    def get_queryset(self):
        # Already filtered by TenantSafeViewSetMixin to their organization
        return Notification.objects.filter(organization=self.request.user.organization)

    def perform_create(self, serializer):
        user = self.request.user
        organization = user.organization
            
        # 1. Save main notification object
        notification = serializer.save(
            organization=organization,
            created_by=user.email
        )
        
        # 2. Distribute to all active members of THIS organization
        users = User.objects.filter(organization=organization, is_active=True)
            
        user_notifications = [
            UserNotification(user=u, notification=notification)
            for u in users
        ]
        UserNotification.objects.bulk_create(user_notifications)

class SuperAdminNotificationViewSet(viewsets.ModelViewSet):
    """
    Super Admin view: Create global notifications or send to specific organizations.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Notification.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        
        # Superadmins can specify an organization in the payload or leave it null for Global
        org_id = self.request.data.get('organization')
        organization = None
        if org_id:
            organization = Organization.objects.filter(id=org_id).first()

        # 1. Save Notification
        notification = serializer.save(
            organization=organization,
            created_by=user.email
        )
        
        # 2. Distribute based on scope
        if organization:
            # Targeted to one organization
            users = User.objects.filter(organization=organization, is_active=True)
        else:
            # Global - sends to everyone!
            users = User.objects.filter(is_active=True)
            
        user_notifications = [
            UserNotification(user=u, notification=notification)
            for u in users
        ]
        UserNotification.objects.bulk_create(user_notifications)
