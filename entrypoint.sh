#!/bin/sh
set -e

echo "Waiting for DB at $DB_HOST:$DB_PORT..."
# Simple TCP wait loop (no extra packages needed)
python - <<'PY'
import os, socket, time
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))
for i in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("DB is reachable.")
            break
    except OSError:
        print(f"DB not reachable yet... ({i+1}/60)")
        time.sleep(2)
else:
    raise SystemExit("DB not reachable, exiting.")
PY

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

echo "Starting server..."
exec "$@"