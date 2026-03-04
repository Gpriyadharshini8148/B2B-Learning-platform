from rest_framework import viewsets, permissions
from admin.access.models import Option
from admin.users.serializers.option_serializer import OptionSerializer

class UserOptionViewSet(viewsets.ReadOnlyModelViewSet):
    """Learner‑side Read-Only view for Option."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OptionSerializer

    def get_queryset(self):
        org = getattr(self.request.user, 'organization', None)
        return Option.objects.filter(organization=org)
