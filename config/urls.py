from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Django JWT Auth + RBAC API",
        default_version='v1',
        description=(
            "A production-ready authentication and role-based access control API built with Django REST Framework.\n\n"
            "## Features\n"
            "- JWT Authentication (Access + Refresh tokens)\n"
            "- Role-Based Access Control (RBAC)\n"
            "- Permission management\n"
            "- Token blacklisting on logout\n"
        ),
        contact=openapi.Contact(email="harshalk1999@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/auth/', include('apps.users.urls', namespace='users')),
    path('api/v1/roles/', include('apps.roles.urls', namespace='roles')),

    # Swagger / ReDoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
