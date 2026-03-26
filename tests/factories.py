import factory
from factory.django import DjangoModelFactory
from apps.users.models import User
from apps.roles.models import Role, Permission


class PermissionFactory(DjangoModelFactory):
    class Meta:
        model = Permission
        django_get_or_create = ('codename',)

    name = factory.Sequence(lambda n: f'Permission {n}')
    codename = factory.Sequence(lambda n: f'resource:action_{n}')
    is_active = True


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'role_{n}')
    description = factory.Faker('sentence')
    is_active = True


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
