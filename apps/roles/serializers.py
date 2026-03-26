from rest_framework import serializers
from .models import Role, Permission


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'description', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Permission.objects.filter(is_active=True),
        source='permissions',
        required=False,
    )
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id', 'name', 'description', 'is_active',
            'permissions', 'permission_ids',
            'user_count', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_user_count(self, obj):
        return obj.users.count()


class AssignRoleSerializer(serializers.Serializer):
    role_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )

    def validate_role_ids(self, value):
        existing = Role.objects.filter(id__in=value, is_active=True).values_list('id', flat=True)
        missing = set(str(v) for v in value) - set(str(e) for e in existing)
        if missing:
            raise serializers.ValidationError(f"Roles not found or inactive: {missing}")
        return value
