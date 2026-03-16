from pathlib import Path
import os
from urllib.parse import urlparse

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def _get_bool_env(name, default="false"):
    return os.getenv(name, default).strip().lower() == "true"


def _get_csv_env(name, default=""):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


def _normalize_allowed_hosts(hosts):
    normalized_hosts = []
    for host in hosts:
        parsed = urlparse(host if "://" in host else f"//{host}")
        normalized_hosts.append(parsed.netloc or parsed.path)
    return normalized_hosts


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Custom club settings
MONTHLY_FEE = 750

# PhonePe Configuration (Sandbox/UAT)
PHONEPE_CONFIG = {
    "CLIENT_ID": "M23VC340MZKCY_2512111424",
    "CLIENT_SECRET": "NDExY2I3YWEtNjc1Ni00ZmFiLTliZWEtYTZiNDNjNjRmZDdk",
    "CLIENT_VERSION": 1,
    "ENV": "SANDBOX",  # Enum: SANDBOX or PRODUCTION
    "CALLBACK_URL": "http://kk11.in/payment/status",  # Update this in production
}


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-2*6kx2b(j3_5-m^!*0lwy086!g+nw378qz$sxbpuymj*zi6hd2",
)

DEBUG = _get_bool_env("DJANGO_DEBUG", "true")

ALLOWED_HOSTS = _normalize_allowed_hosts(
    _get_csv_env(
        "DJANGO_ALLOWED_HOSTS",
        "72.61.243.80,localhost,127.0.0.1,kk11.in,www.kk11.in,api.kk11.in",
    )
)

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "financials",
    "players",
    "teams",
    "matches",
    "inventory",
    "tournaments",
    "grounds",
    "media_gallery",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cricket_club.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cricket_club.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

database_url = os.getenv("DATABASE_URL")

if database_url:
    DATABASES = {
        "default": dj_database_url.parse(database_url, conn_max_age=60),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.mysql"),
            "NAME": os.getenv("DB_NAME", "club_management"),
            "USER": os.getenv("DB_USER", "club_user"),
            "PASSWORD": os.getenv("DB_PASSWORD", "club_password"),
            "HOST": os.getenv("DB_HOST", "db"),
            "PORT": os.getenv("DB_PORT", "3306"),
            "CONN_MAX_AGE": 60,
            "OPTIONS": {
                "connect_timeout": 10,
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
        }
    }


# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# CORS settings
CORS_ALLOW_ALL_ORIGINS = _get_bool_env("DJANGO_CORS_ALLOW_ALL_ORIGINS", "false")
CORS_ALLOWED_ORIGINS = _get_csv_env(
    "DJANGO_CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,https://kk11.in,https://www.kk11.in,https://api.kk11.in",
)

CSRF_TRUSTED_ORIGINS = _get_csv_env(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://72.61.243.80,http://localhost:3000,http://127.0.0.1:3000,https://kk11.in,https://www.kk11.in,https://api.kk11.in",
)
# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Cricket Club API',
    'DESCRIPTION': 'API for managing players, teams, matches, and more.',
    'VERSION': '1.0.0',
}
