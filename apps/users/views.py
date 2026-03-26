from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    TokenResponseSerializer,
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={201: TokenResponseSerializer},
        operation_summary="Register a new user",
        tags=['Auth'],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: TokenResponseSerializer},
        operation_summary="Login and get JWT tokens",
        tags=['Auth'],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            **tokens,
            'user': UserProfileSerializer(user).data,
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={205: 'Token blacklisted successfully'},
        operation_summary="Logout (blacklist refresh token)",
        tags=['Auth'],
    )
    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserProfileSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        responses={200: UserProfileSerializer},
        operation_summary="Get current user profile",
        tags=['Profile'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={200: UserProfileSerializer},
        operation_summary="Update profile (full)",
        tags=['Profile'],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=UserUpdateSerializer,
        responses={200: UserProfileSerializer},
        operation_summary="Update profile (partial)",
        tags=['Profile'],
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={200: 'Password changed successfully'},
        operation_summary="Change password",
        tags=['Profile'],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    """Admin: list all users."""
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        from apps.roles.permissions import IsAdminRole
        # Only admins can list users
        if not self.request.user.has_role('admin'):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only admins can list users.')
        return User.objects.prefetch_related('roles').all()

    @swagger_auto_schema(
        operation_summary="[Admin] List all users",
        tags=['Admin'],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
