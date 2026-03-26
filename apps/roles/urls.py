from django.urls import path
from .views import (
    PermissionListCreateView,
    PermissionDetailView,
    RoleListCreateView,
    RoleDetailView,
    UserRoleAssignView,
)

app_name = 'roles'

urlpatterns = [
    # Permissions
    path('permissions/', PermissionListCreateView.as_view(), name='permission-list'),
    path('permissions/<uuid:pk>/', PermissionDetailView.as_view(), name='permission-detail'),

    # Roles
    path('', RoleListCreateView.as_view(), name='role-list'),
    path('<uuid:pk>/', RoleDetailView.as_view(), name='role-detail'),

    # Assign / remove roles to/from a user
    path('users/<uuid:user_id>/assign/', UserRoleAssignView.as_view(), name='user-role-assign'),
]
