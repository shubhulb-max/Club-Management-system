from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


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
    "CALLBACK_URL": "http://72.61.243.80:8000/payment/status",  # Update this in production
}


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-2*6kx2b(j3_5-m^!*0lwy086!g+nw378qz$sxbpuymj*zi6hd2",
)

DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() == "true"

ALLOWED_HOSTS = ["72.61.243.80", "localhost", "127.0.0.1","kk11.in","api.kk11.in"]

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
    "rest_framework.authtoken",
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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "club_management",
        "USER": "club_user",
        "PASSWORD": "club_password",
        "HOST": "db",
        "PORT": "3306",
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
cors_allow_all_origins = os.getenv("DJANGO_CORS_ALLOW_ALL_ORIGINS", "false").lower() == "true"
CORS_ALLOW_ALL_ORIGINS = cors_allow_all_origins

cors_allowed_origins = os.getenv("DJANGO_CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [
    origin for origin in cors_allowed_origins.split(",") if origin
] or ["http://localhost:3000", "http://club-management-system-006z.onrender.com","https://kk11.in"]

CSRF_TRUSTED_ORIGINS = [
    "http://72.61.243.80",
    "http://localhost:3000",
]
# DRF settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Cricket Club API',
    'DESCRIPTION': 'API for managing players, teams, matches, and more.',
    'VERSION': '1.0.0',
}
