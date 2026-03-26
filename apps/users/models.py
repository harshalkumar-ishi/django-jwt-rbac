from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # RBAC — roles assigned to this user
    roles = models.ManyToManyField(
        'roles.Role',
        blank=True,
        related_name='users',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return self.roles.filter(name=role_name, is_active=True).exists()

    def has_permission_code(self, codename: str) -> bool:
        """Check if user has a specific permission via any of their roles."""
        return self.roles.filter(
            is_active=True,
            permissions__codename=codename,
            permissions__is_active=True,
        ).exists()

    def get_all_permissions_list(self):
        """Return a flat list of all permission codenames for this user."""
        return list(
            self.roles.filter(is_active=True)
            .values_list('permissions__codename', flat=True)
            .distinct()
        )
