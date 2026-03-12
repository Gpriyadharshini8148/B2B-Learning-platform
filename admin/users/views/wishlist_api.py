from rest_framework import views, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from admin.access.models import Wishlist, Course
from ..serializers.wishlist_serializer import WishlistSerializer
from ..serializers.wishlist_toggle_serializer import WishlistToggleSerializer

class WishlistToggleAPIView(views.APIView):
    """
    POST /api/users/wishlist
    Request Body: { "course_id": <int> }
    
    Toggles the course in user's wishlist.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=WishlistToggleSerializer,
        responses={200: dict, 201: dict, 400: dict, 404: dict},
        operation_id="api_users_wishlist_toggle"
    )
    def post(self, request):
        serializer = WishlistToggleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        course_id = serializer.validated_data.get('course_id')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item = Wishlist.objects.filter(user=request.user, course=course).first()

        if wishlist_item:
            wishlist_item.delete()
            return Response({
                "message": "Course removed from wishlist",
                "course_id": course_id
            }, status=status.HTTP_200_OK)
        else:
            Wishlist.objects.create(user=request.user, course=course)
            return Response({
                "message": "Course added to wishlist",
                "course_id": course_id
            }, status=status.HTTP_201_CREATED)

class WishlistListAPIView(views.APIView):
    """
    GET /api/users/wishlist
    
    Returns the list of wishlisted courses for the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: WishlistSerializer(many=True)},
        operation_id="api_users_wishlist_list"
    )
    def get(self, request):
        wishlist_items = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
