#!/usr/bin/env bash
# exit on error
set -o errexit

# Upgrade pip to latest version
python -m pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser automatically if not exists
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@pdvsystem.com', 'admin123')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
END
