# -------- Base image --------
FROM python:3.12

# -------- Python runtime env --------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -------- OS deps --------
# - mysqlclient build deps: default-libmysqlclient-dev, build-essential, pkg-config
# - netcat-openbsd: optional, useful for DB port check (if you use nc in entrypoint)
# - curl: optional
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -------- Install pip tooling first --------
# pkg_resources comes from setuptools (needed by apscheduler/phonepe dependency chain)
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel

# -------- Install dependencies --------
COPY requirements.txt /app/requirements.txt

# Install your requirements
RUN python -m pip install --no-cache-dir -r requirements.txt

# Force correct mysqlclient version (Django requires >=2.2.1)
RUN python -m pip uninstall -y mysqlclient || true \
    && python -m pip install --no-cache-dir "mysqlclient>=2.2.1"

# Install gunicorn
RUN python -m pip install --no-cache-dir gunicorn

# Verify critical imports at build time (fails build if missing)
RUN python -c "import pkg_resources; print('pkg_resources OK')" \
    && python -c "import MySQLdb; print('mysqlclient OK')" \
    && python -c "import pkg_resources; print('mysqlclient version:', pkg_resources.get_distribution('mysqlclient').version)"

# -------- Copy project files --------
COPY . /app

# -------- Entrypoint --------
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# Use env var for WSGI module if you want:
# DJANGO_WSGI_MODULE=cricket_club.wsgi:application
CMD ["sh", "-c", "gunicorn ${DJANGO_WSGI_MODULE:-cricket_club.wsgi:application} --bind 0.0.0.0:8000 --workers 3 --timeout 120"]