from rest_framework import views, status, permissions
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from drf_spectacular.utils import extend_schema
from admin.organizations.serializers.invitation_serializer import InviteUserSerializer, AcceptInvitationSerializer
from admin.organizations.models.invitation import Invitation
from admin.access.models.user import User
from admin.access.models.role import Role
from admin.access.models.user_role import UserRole

class OrgInviteNewUserView(views.APIView):
    """
    API for Organization admins to invite a user to their organization.
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=InviteUserSerializer)
    def post(self, request):
        user = request.user
        if not user.organization:
            return Response({"error": "User does not belong to any organization."}, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get('email')
        role_name = request.data.get('role', 'learner')

        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update invitation
        invitation, created = Invitation.objects.update_or_create(
            email=email,
            organization=user.organization,
            defaults={'is_used': False, 'role': role_name}
        )

        # Ensure we have the base URL from the request for the API endpoint
        base_url = request.build_absolute_uri('/')[:-1] # Remove trailing slash
        invite_url = f"{base_url}/api/organizations/accept-invite/?token={invitation.token}"
        
        return Response({
            "message": f"Invitation created for {email}. Access link: {invite_url}",
            "invite_url": invite_url 
        }, status=status.HTTP_200_OK)


class AcceptInvitationView(views.APIView):
    """
    API for users to accept an invitation and complete their signup.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=AcceptInvitationSerializer, responses={200: dict})
    def post(self, request):
        token = request.data.get('token') or request.query_params.get('token')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        password = request.data.get('password')

        if not token or not password:
            return Response({"error": "token and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        if not invitation.is_valid():
            return Response({"error": "Invitation has expired or been used already."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already registered via another path
        if User.objects.filter(email=invitation.email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        user = User.objects.create(
            email=invitation.email,
            password_hash=make_password(password),
            first_name=first_name,
            last_name=last_name,
            organization=invitation.organization,
            is_active=True,
            approval_status='approved'
        )

        # Assign Role
        role, _ = Role.objects.get_or_create(
            name=invitation.role,
            organization=invitation.organization,
            defaults={"description": f"{invitation.role.capitalize()} role"}
        )
        UserRole.objects.create(user=user, role=role)

        # Mark invitation as used
        invitation.is_used = True
        invitation.save()

        return Response({
            "message": "User registered successfully and linked to organization. You can now login.",
        }, status=status.HTTP_201_CREATED)
