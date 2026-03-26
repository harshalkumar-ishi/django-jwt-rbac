"""
Management command to seed default roles and permissions.
Usage: python manage.py seed_roles
"""
from django.core.management.base import BaseCommand
from apps.roles.models import Role, Permission


PERMISSIONS = [
    # User management
    ('user:list',   'Can list users'),
    ('user:create', 'Can create users'),
    ('user:update', 'Can update users'),
    ('user:delete', 'Can delete users'),
    # Role management
    ('role:list',   'Can list roles'),
    ('role:create', 'Can create roles'),
    ('role:update', 'Can update roles'),
    ('role:delete', 'Can delete roles'),
    # Content
    ('content:read',   'Can read content'),
    ('content:write',  'Can write content'),
    ('content:delete', 'Can delete content'),
]

ROLES = {
    'admin': {
        'description': 'Full system access',
        'permissions': [p[0] for p in PERMISSIONS],
    },
    'editor': {
        'description': 'Can manage content',
        'permissions': ['content:read', 'content:write', 'user:list'],
    },
    'viewer': {
        'description': 'Read-only access',
        'permissions': ['content:read'],
    },
}


class Command(BaseCommand):
    help = 'Seed default roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Seeding permissions...')
        perm_map = {}
        for codename, name in PERMISSIONS:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={'name': name},
            )
            perm_map[codename] = perm
            status = 'created' if created else 'exists'
            self.stdout.write(f'  [{status}] {codename}')

        self.stdout.write('Seeding roles...')
        for role_name, config in ROLES.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': config['description']},
            )
            perms = [perm_map[c] for c in config['permissions']]
            role.permissions.set(perms)
            status = 'created' if created else 'updated'
            self.stdout.write(f'  [{status}] {role_name} ({len(perms)} permissions)')

        self.stdout.write(self.style.SUCCESS('✅ Seed complete!'))
