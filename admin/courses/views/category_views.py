from rest_framework import viewsets, permissions
from ..models.category import Category
from ..serializers.category_serializer import CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
