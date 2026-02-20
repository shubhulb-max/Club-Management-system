# Use Python 3.12
FROM python:3.12-slim

# Prevent .pyc + make logs unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system deps:
# - default-libmysqlclient-dev + build-essential + pkg-config => mysqlclient build
# - netcat-openbsd => (optional) useful for DB wait checks
# - curl => optional
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project
COPY . .

# Entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Use env var for WSGI module (set in docker-compose/.env):
# DJANGO_WSGI_MODULE=yourproject.wsgi:application
CMD ["sh", "-c", "gunicorn ${DJANGO_WSGI_MODULE:-YOUR_PROJECT_NAME.wsgi:application} --bind 0.0.0.0:8000 --workers 3 --timeout 120"]