from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from ..models.organization import Organization
from ..serializers.organization_serializer import OrganizationSerializer
from ...access.permissions.tenant_permissions import IsSuperAdmin, IsOrganizationAdmin

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Organizations.
    Super Admins: Full management.
    Org Admins: Can only see/update their own organization.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_permissions(self):
        # Allow Org Admins to 'list' (their own org) and 'retrieve'/'update'
        if self.action in ['create', 'destroy']:
            return [IsSuperAdmin()]
        return [IsOrganizationAdmin()]

    def get_queryset(self):
        user = self.request.user
        
        # Super Admin / Staff check
        super_admin_email = getattr(settings, 'EMAIL_HOST_USER', 'gpriyadharshini9965@gmail.com')
        if user.is_superuser or getattr(user, 'email', '') == super_admin_email or user.is_staff:
            return Organization.objects.all()
            
        # Extract organization using our custom model mapping (since we fixed this globally)
        org_id = getattr(user, 'organization_id', None)
        return Organization.objects.filter(id=org_id)


    @action(detail=False, methods=['GET', 'PATCH', 'PUT'])
    def me(self, request):
        """
        Returns the organization profile for the logged-in Org Admin.
        """
        user = request.user
        # Querying by id ensures we get the specific org even if it's inactive
        org_id = getattr(user, 'organization_id', None)
        if not org_id:
             return Response({"detail": "User has no organization associated."}, status=400)
             
        org = Organization.objects.get(id=org_id)
        if request.method == 'GET':
            serializer = self.get_serializer(org)
            return Response(serializer.data)
        
        # Support updates
        serializer = self.get_serializer(org, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
