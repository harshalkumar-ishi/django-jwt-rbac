from django.db import models
import uuid


class Permission(models.Model):
    """
    A granular permission that can be assigned to roles.
    e.g. codename='user:create', name='Can create users'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'permissions'
        ordering = ['codename']

    def __str__(self):
        return f"{self.codename} — {self.name}"


class Role(models.Model):
    """
    A named collection of permissions.
    e.g. admin, editor, viewer
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_permissions_list(self):
        return list(self.permissions.filter(is_active=True).values_list('codename', flat=True))
