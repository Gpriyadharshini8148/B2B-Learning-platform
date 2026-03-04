from rest_framework import viewsets, permissions
from admin.access.models.category import Category
from admin.organizations.serializers.category_serializer import CategorySerializer

class StudentCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/users/categories
    List categories belonging to the user's organization.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        organization = getattr(user, 'organization', None)
        
        # Filter categories by the user's current organization
        # We also ensure the category is active and not deleted
        return Category.objects.filter(
            organization=organization,
            is_active=True,
            is_deleted=False
        )
