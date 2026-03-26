#!/bin/sh

set -e

echo "=================================================="
echo "  Django JWT Auth + RBAC — Startup Script"
echo "=================================================="

# ── 1. Wait for PostgreSQL to be ready ────────────────
echo "\n[1/5] Waiting for PostgreSQL..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        dbname=os.environ.get('DB_NAME','jwt_rbac_db'),
        user=os.environ.get('DB_USER','postgres'),
        password=os.environ.get('DB_PASSWORD','postgres'),
        host=os.environ.get('DB_HOST','db'),
        port=os.environ.get('DB_PORT','5432'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "   PostgreSQL not ready yet — retrying in 2s..."
  sleep 2
done
echo "   ✅ PostgreSQL is ready!"

# ── 2. Create migrations if missing ───────────────────
echo "\n[2/5] Creating migrations (if needed)..."
python manage.py makemigrations users --no-input
python manage.py makemigrations roles --no-input
python manage.py makemigrations --no-input
echo "   ✅ Migrations ready!"

# ── 3. Apply migrations ───────────────────────────────
echo "\n[3/5] Applying migrations..."
python manage.py migrate --no-input
echo "   ✅ Migrations applied!"

# ── 4. Seed default roles & permissions ───────────────
echo "\n[4/5] Seeding roles and permissions..."
python manage.py seed_roles
echo "   ✅ Seed complete!"

# ── 5. Collect static files ───────────────────────────
echo "\n[5/5] Collecting static files..."
python manage.py collectstatic --no-input --clear
echo "   ✅ Static files collected!"

echo "\n=================================================="
echo "  ✅ Setup complete! Starting Django server..."
echo "  📍 API:     http://localhost:8000/api/v1/"
echo "  📖 Swagger: http://localhost:8000/swagger/"
echo "  ⚙️  Admin:   http://localhost:8000/admin/"
echo "=================================================="

# ── Start server ──────────────────────────────────────
exec python manage.py runserver 0.0.0.0:8000