# -------- Base image (Stable for PhonePe SDK) --------
FROM python:3.12.6-bookworm

# -------- Python runtime env --------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -------- OS dependencies --------
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    netcat-openbsd \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# -------- Upgrade pip tooling --------
# pkg_resources comes from setuptools (required by apscheduler used inside PhonePe SDK)
RUN python -m pip install --no-cache-dir --upgrade \
    pip==24.2 \
    setuptools==75.1.0 \
    wheel

# -------- Copy requirements --------
COPY requirements.txt .

# -------- Install dependencies --------
RUN python -m pip install --no-cache-dir -r requirements.txt

# -------- Force compatible APScheduler (important for PhonePe) --------
# Some newer versions cause issues
RUN python -m pip install --no-cache-dir "apscheduler==3.10.1"

# -------- Ensure mysqlclient version compatible with Django --------
RUN python -m pip uninstall -y mysqlclient || true \
    && python -m pip install --no-cache-dir "mysqlclient>=2.2.4"

# -------- Install Gunicorn --------
RUN python -m pip install --no-cache-dir gunicorn==21.2.0

# -------- Verify critical imports at build time --------
RUN python -c "import pkg_resources; print('pkg_resources OK')" \
    && python -c "import apscheduler; print('apscheduler OK')" \
    && python -c "import MySQLdb; print('mysqlclient OK')" \
    && python -c "from phonepe.sdk.pg.payments.v2.standard_checkout_client import StandardCheckoutClient; print('PhonePe SDK OK')"

# -------- Copy project files --------
COPY . .

# -------- Entrypoint --------
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sh", "-c", "gunicorn ${DJANGO_WSGI_MODULE:-cricket_club.wsgi:application} --bind 0.0.0.0:8000 --workers 3 --timeout 120"]
