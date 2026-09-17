"""
Django settings for the auth backend (JWT + Email OTP).
"""
from pathlib import Path
from datetime import timedelta
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="192.168.0.120, .onrender.com, .railway.app, localhost,",
    cast=Csv(),
)

FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

# Base URL used when building links inside emails (e.g. a "click to verify"
# link, if you add one later). Falls back to FRONTEND_URL if not set.
EMAIL_PAGE_DOMAIN = config("EMAIL_PAGE_DOMAIN", default=FRONTEND_URL)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",

    "accounts",
    "blog",
    "reviews",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Database credentials come from the environment. Set DB_ENGINE=sqlite in
# .env to develop against a local file instead of the hosted Postgres.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "neondb",
        "USER": "neondb_owner",
        "PASSWORD": "npg_4YDBNQ0hylng",
        "HOST": "ep-long-water-aencaknp-pooler.c-2.us-east-2.aws.neon.tech",
        "HOST":"ep-bold-waterfall-b49heore-pooler.c-6.us-east-2.aws.neon.tech",
        "PORT": "5432",
        "OPTIONS": {
            "sslmode": "require",
            "channel_binding": "require",
        },
    }
}
# else:
#     DATABASES = {
#         "default": {
#             "ENGINE": "django.db.backends.postgresql",
#             "NAME": config("DB_NAME", default="neondb"),
#             "USER": config("DB_USER", default=""),
#             "PASSWORD": config("DB_PASSWORD", default=""),
#             "HOST": config("DB_HOST", default=""),
#             "PORT": config("DB_PORT", default="5432"),
#             "OPTIONS": {
#                 "sslmode": config("DB_SSLMODE", default="require"),
#             },
#         }
#     }
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------- Uploads ----------------
# Largest cover image a blog author may upload, in bytes (default 5MB).
BLOG_COVER_MAX_BYTES = config("BLOG_COVER_MAX_BYTES", default=5 * 1024 * 1024, cast=int)
# Anything above this is streamed to a temp file rather than held in memory.
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = BLOG_COVER_MAX_BYTES + (1024 * 1024)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- REST FRAMEWORK ----------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------- CORS / CSRF ----------------
# Includes the LAN IP so the frontend can also be reached at
# http://192.168.0.104:3000 (e.g. testing from another device on the network).
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default=f"{FRONTEND_URL},http://192.168.0.120:3000,http://192.168.0.120:3000",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# ---------------- EMAIL (Gmail SMTP) ----------------
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = 'rajkumararyal0977@gmail.com'
EMAIL_HOST_PASSWORD = 'pnierfurujtkbsbe'
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default=EMAIL_HOST_USER)

# If no Gmail creds are set, fall back to printing emails to the console
# so registration still works during local development.
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

OTP_EXPIRY_MINUTES = config("OTP_EXPIRY_MINUTES", default=10, cast=int)

# ---------------- Auth redirects ----------------
# NOTE: this project's login is a JWT REST API (see accounts/urls.py), not
# Django's session-based auth views, so these two settings aren't consulted
# anywhere in the current flow. They're included because you asked for them
# and are harmless to have set — but if you want a traditional server-rendered
# login/redirect (e.g. for the Django admin app under a custom namespace),
# you'd need to add a URL named "otp_auth:login" and "otp_auth:success" for
# these to resolve correctly.
LOGIN_URL = config("LOGIN_URL", default="otp_auth:login")
LOGIN_REDIRECT_URL = config("LOGIN_REDIRECT_URL", default="otp_auth:success")
