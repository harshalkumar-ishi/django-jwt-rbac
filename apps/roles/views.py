from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Role, Permission
from .serializers import RoleSerializer, PermissionSerializer, AssignRoleSerializer
from .permissions import IsAdminRole
from apps.users.models import User


# ── Permissions CRUD ──────────────────────────────────────────────────────────

class PermissionListCreateView(generics.ListCreateAPIView):
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated, IsAdminRole)
    queryset = Permission.objects.all()

    @swagger_auto_schema(operation_summary="[Admin] List all permissions", tags=['Roles & Permissions'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PermissionSerializer,
        operation_summary="[Admin] Create a permission",
        tags=['Roles & Permissions'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated, IsAdminRole)
    queryset = Permission.objects.all()

    @swagger_auto_schema(operation_summary="[Admin] Get a permission", tags=['Roles & Permissions'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PermissionSerializer,
        operation_summary="[Admin] Update a permission",
        tags=['Roles & Permissions'],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="[Admin] Delete a permission", tags=['Roles & Permissions'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ── Roles CRUD ────────────────────────────────────────────────────────────────

class RoleListCreateView(generics.ListCreateAPIView):
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated, IsAdminRole)
    queryset = Role.objects.prefetch_related('permissions').all()

    @swagger_auto_schema(operation_summary="[Admin] List all roles", tags=['Roles & Permissions'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RoleSerializer,
        operation_summary="[Admin] Create a role",
        tags=['Roles & Permissions'],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated, IsAdminRole)
    queryset = Role.objects.prefetch_related('permissions').all()

    @swagger_auto_schema(operation_summary="[Admin] Get a role", tags=['Roles & Permissions'])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=RoleSerializer,
        operation_summary="[Admin] Update a role",
        tags=['Roles & Permissions'],
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="[Admin] Delete a role", tags=['Roles & Permissions'])
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


# ── Assign / Remove roles from a user ────────────────────────────────────────

class UserRoleAssignView(APIView):
    permission_classes = (IsAuthenticated, IsAdminRole)

    def get_user(self, pk):
        try:
            return User.objects.prefetch_related('roles').get(pk=pk)
        except User.DoesNotExist:
            return None

    @swagger_auto_schema(
        request_body=AssignRoleSerializer,
        responses={200: 'Roles assigned successfully'},
        operation_summary="[Admin] Assign roles to a user",
        tags=['User Role Management'],
    )
    def post(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        roles = Role.objects.filter(id__in=serializer.validated_data['role_ids'])
        user.roles.add(*roles)
        return Response({
            'detail': 'Roles assigned.',
            'roles': RoleSerializer(user.roles.all(), many=True).data,
        })

    @swagger_auto_schema(
        request_body=AssignRoleSerializer,
        responses={200: 'Roles removed successfully'},
        operation_summary="[Admin] Remove roles from a user",
        tags=['User Role Management'],
    )
    def delete(self, request, user_id):
        user = self.get_user(user_id)
        if not user:
            return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        roles = Role.objects.filter(id__in=serializer.validated_data['role_ids'])
        user.roles.remove(*roles)
        return Response({
            'detail': 'Roles removed.',
            'roles': RoleSerializer(user.roles.all(), many=True).data,
        })
