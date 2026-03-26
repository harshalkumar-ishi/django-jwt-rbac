# 🔑 Django JWT Auth + RBAC

A production-ready **Authentication & Role-Based Access Control** REST API built with Django REST Framework, SimpleJWT, PostgreSQL, and Docker.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-green?logo=django)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![JWT](https://img.shields.io/badge/Auth-JWT-orange)

---

## 📌 Features

- ✅ **JWT Authentication** — Access + Refresh tokens via `djangorestframework-simplejwt`
- ✅ **Token Blacklisting** — Secure logout invalidates refresh tokens
- ✅ **Role-Based Access Control (RBAC)** — Users → Roles → Permissions
- ✅ **Custom User Model** — UUID primary keys, email-based auth
- ✅ **Swagger UI + ReDoc** — Full interactive API documentation
- ✅ **Docker + PostgreSQL** — One-command setup
- ✅ **Seed Command** — Pre-loads default roles (`admin`, `editor`, `viewer`) and permissions
- ✅ **Pytest Suite** — Auth, profile, and RBAC tests with Factory Boy

---

## 🏗️ Project Structure

```
django-jwt-rbac/
├── apps/
│   ├── users/               # Custom user model, auth endpoints
│   │   ├── models.py        # User model with RBAC helpers
│   │   ├── serializers.py   # Register, Login, Profile serializers
│   │   ├── views.py         # Register, Login, Logout, Profile views
│   │   ├── urls.py
│   │   └── admin.py
│   └── roles/               # RBAC — Roles & Permissions
│       ├── models.py        # Role, Permission models
│       ├── serializers.py
│       ├── views.py         # CRUD + user role assignment
│       ├── permissions.py   # Custom DRF permission classes
│       ├── urls.py
│       ├── admin.py
│       └── management/
│           └── commands/
│               └── seed_roles.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tests/
│   ├── factories.py
│   └── test_auth.py
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/harshalkumar-ishi/django-jwt-rbac.git
cd django-jwt-rbac
cp .env.example .env
```

### 2. Run with Docker

```bash
docker-compose up --build
```

This will:
- Start PostgreSQL
- Run `migrate`
- Seed default roles & permissions
- Start the Django dev server on **http://localhost:8000**

### 3. Create a superuser (optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

---

## 📖 API Documentation

| URL | Description |
|-----|-------------|
| `http://localhost:8000/swagger/` | Swagger UI |
| `http://localhost:8000/redoc/`   | ReDoc |
| `http://localhost:8000/admin/`   | Django Admin |

---

## 🔗 API Endpoints

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/v1/auth/register/` | ❌ | Register new user |
| `POST` | `/api/v1/auth/login/` | ❌ | Login, get tokens |
| `POST` | `/api/v1/auth/logout/` | ✅ | Blacklist refresh token |
| `POST` | `/api/v1/auth/token/refresh/` | ❌ | Refresh access token |
| `GET`  | `/api/v1/auth/profile/` | ✅ | Get current user profile |
| `PATCH`| `/api/v1/auth/profile/` | ✅ | Update profile |
| `POST` | `/api/v1/auth/profile/change-password/` | ✅ | Change password |
| `GET`  | `/api/v1/auth/users/` | ✅ Admin | List all users |

### Roles & Permissions (Admin only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/v1/roles/` | List / Create roles |
| `GET/PUT/DELETE` | `/api/v1/roles/<id>/` | Retrieve / Update / Delete role |
| `GET/POST` | `/api/v1/roles/permissions/` | List / Create permissions |
| `GET/PUT/DELETE` | `/api/v1/roles/permissions/<id>/` | Retrieve / Update / Delete permission |
| `POST` | `/api/v1/roles/users/<user_id>/assign/` | Assign roles to user |
| `DELETE` | `/api/v1/roles/users/<user_id>/assign/` | Remove roles from user |

---

## 🔐 RBAC Architecture

```
User  ──(many-to-many)──▶  Role  ──(many-to-many)──▶  Permission
                           admin                        user:create
                           editor                       content:write
                           viewer                       content:read
```

### Default Roles (seeded automatically)

| Role | Permissions |
|------|-------------|
| `admin` | All permissions |
| `editor` | `content:read`, `content:write`, `user:list` |
| `viewer` | `content:read` |

### Custom Permission Classes

```python
from apps.roles.permissions import IsAdminRole, IsEditorRole, require_permission

class MyView(APIView):
    # Option 1 — role check
    permission_classes = [IsAuthenticated, IsAdminRole]

    # Option 2 — permission codename check
    permission_classes = [IsAuthenticated, require_permission('content:write')]
```

### User helper methods

```python
user.has_role('admin')                    # → True / False
user.has_permission_code('user:delete')   # → True / False
user.get_all_permissions_list()           # → ['user:list', 'content:read', ...]
```

---

## 🧪 Running Tests

```bash
# Inside Docker
docker-compose exec web pytest

# Locally (with venv)
pip install -r requirements.txt
pytest
```

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 4.2, Django REST Framework 3.15 |
| Auth | djangorestframework-simplejwt 5.3 |
| Database | PostgreSQL 15 |
| Containerisation | Docker, Docker Compose |
| Docs | drf-yasg (Swagger + ReDoc) |
| Testing | pytest-django, factory-boy |
| Config | python-decouple |

---

## 📄 License

MIT — feel free to use this as a starter for your own projects.

---

*Built by [Harshalkumar Ishi](https://github.com/harshalkumar-ishi)*
