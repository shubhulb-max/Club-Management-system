#!/bin/sh
set -e

echo "Waiting for database..."
until python manage.py check --database default >/dev/null 2>&1; do
  sleep 1
done

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
