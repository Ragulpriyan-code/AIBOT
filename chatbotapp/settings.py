import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env in development only
load_dotenv(BASE_DIR / ".env")

"""
Django settings for chatbotapp project.
"""

# ====================================================
# SECURITY
# ====================================================

# Prevent empty key crash in Render
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "unsafe-dev-key-change-this"
)

DEBUG = os.environ.get("DEBUG", "False") == "True"


ALLOWED_HOSTS = [
    ".onrender.com",
    ".railway.app",
    "localhost",
    "127.0.0.1",
    "*",  # Allow all hosts (remove in production for better security)
]

# ====================================================
# APPLICATION DEFINITION
# ====================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # YOUR CHATBOT APP
    "chatbot",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # RENDER STATIC HANDLING
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "chatbotapp.urls"
WSGI_APPLICATION = "chatbotapp.wsgi.application"

# ====================================================
# DATABASE — RENDER OVERRIDE + LOCAL FALLBACK
# ====================================================
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "unsafe-dev-key-change-this"
)
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }
else:
    # LOCAL DEVELOPMENT FALLBACK (SAFE)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ====================================================
# TEMPLATES
# ====================================================

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

# ====================================================
# PASSWORD VALIDATION
# ====================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ====================================================
# INTERNATIONALIZATION
# ====================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ====================================================
# STATIC FILES
# ====================================================

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ====================================================
# LOGIN / LOGOUT LOGIC — KEEP
# ====================================================

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/login/"

# ====================================================
# DEFAULT PK FIELD
# ====================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
