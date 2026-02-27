from rest_framework import viewsets, permissions
from ..models.permission import Permission
from ..serializers.permission_serializer import PermissionSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAdminUser]
