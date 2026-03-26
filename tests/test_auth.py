import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from tests.factories import UserFactory, RoleFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def admin_user(db):
    admin_role = RoleFactory(name='admin')
    user = UserFactory()
    user.roles.add(admin_role)
    return user


def auth_client(user):
    client = APIClient()
    response = client.post(reverse('users:login'), {
        'email': user.email,
        'password': 'testpass123',
    }, format='json')
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
    return client, response.data['refresh']


# ── Register ──────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRegister:
    url = '/api/v1/auth/register/'

    def test_register_success(self, client):
        data = {
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
        }
        response = client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'new@example.com'

    def test_register_password_mismatch(self, client):
        data = {
            'email': 'new@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123',
            'password_confirm': 'different123',
        }
        response = client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, client, user):
        data = {
            'email': user.email,
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'strongpass123',
            'password_confirm': 'strongpass123',
        }
        response = client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Login ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLogin:
    url = '/api/v1/auth/login/'

    def test_login_success(self, client, user):
        response = client.post(self.url, {
            'email': user.email, 'password': 'testpass123'
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_wrong_password(self, client, user):
        response = client.post(self.url, {
            'email': user.email, 'password': 'wrongpassword'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self, client):
        response = client.post(self.url, {
            'email': 'ghost@example.com', 'password': 'whatever'
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ── Logout ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestLogout:
    url = '/api/v1/auth/logout/'

    def test_logout_success(self, user):
        authed_client, refresh = auth_client(user)
        response = authed_client.post(self.url, {'refresh': refresh}, format='json')
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_invalid_token(self, user):
        authed_client, _ = auth_client(user)
        response = authed_client.post(self.url, {'refresh': 'invalid-token'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_requires_auth(self, client):
        response = client.post(self.url, {'refresh': 'whatever'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── Profile ───────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestProfile:
    url = '/api/v1/auth/profile/'

    def test_get_profile(self, user):
        authed_client, _ = auth_client(user)
        response = authed_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_update_profile(self, user):
        authed_client, _ = auth_client(user)
        response = authed_client.patch(self.url, {
            'first_name': 'Updated',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_profile_requires_auth(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ── RBAC ──────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRBAC:
    roles_url = '/api/v1/roles/'

    def test_non_admin_cannot_list_roles(self, user):
        authed_client, _ = auth_client(user)
        response = authed_client.get(self.roles_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_list_roles(self, admin_user):
        authed_client, _ = auth_client(admin_user)
        response = authed_client.get(self.roles_url)
        assert response.status_code == status.HTTP_200_OK

    def test_has_role_method(self, db):
        role = RoleFactory(name='editor')
        user = UserFactory()
        assert not user.has_role('editor')
        user.roles.add(role)
        assert user.has_role('editor')
