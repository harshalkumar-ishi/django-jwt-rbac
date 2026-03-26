from django.contrib import admin
from .models import Role, Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('codename', 'name')
    ordering = ('codename',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'user_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    ordering = ('name',)

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'
