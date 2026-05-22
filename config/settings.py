"""
SecureTask — Django Settings
Aligned with OWASP Top 10 and OWASP ASVS security controls.
"""

import os
from pathlib import Path
from decouple import config

# ─── Base ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: SECRET_KEY loaded from environment — never hardcoded
# OWASP A02: Cryptographic Failures
SECRET_KEY = config('SECRET_KEY', default='change-me-in-production')

# SECURITY: DEBUG must be False in production — disables stack traces
# OWASP A05: Security Misconfiguration
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# ─── Apps ────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework.authtoken',
    'axes',            # Brute-force protection — OWASP A07
    'csp',             # Content Security Policy headers
    # Local apps
    'accounts',
    'tasks',
    'api',
]

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Static file serving
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # SECURITY: CSRF middleware — OWASP A01, prevents cross-site request forgery
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # SECURITY: Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Content Security Policy
    'csp.middleware.CSPMiddleware',
    # Brute-force tracking
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            # SECURITY: Autoescaping ON by default — prevents XSS
            # OWASP A03: Injection
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ─── Database — MySQL ─────────────────────────────────────────────────────────
# SECURITY: Credentials from environment variables — OWASP A02
# SECURITY: ORM only — prevents SQL injection — OWASP A03
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME':     config('DB_NAME',     default='securetask_db'),
        'USER':     config('DB_USER',     default='root'),
        'PASSWORD': config('DB_PASSWORD', default='root'),
        'HOST':     config('DB_HOST',     default='127.0.0.1'),
        'PORT':     config('DB_PORT',     default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ─── Password Validation ──────────────────────────────────────────────────────
# SECURITY: Strong password policy — OWASP A07: Identification & Auth Failures
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Session Security ─────────────────────────────────────────────────────────
# SECURITY: Session timeout — OWASP A07
SESSION_COOKIE_AGE           = 1800          # 30 minutes inactivity timeout
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST   = True          # Refresh session on activity

# SECURITY: Secure session cookie — prevent JS access
SESSION_COOKIE_HTTPONLY      = True
SESSION_COOKIE_SAMESITE      = 'Lax'
SESSION_COOKIE_SECURE        = config('SESSION_COOKIE_SECURE', default=False, cast=bool)

# ─── CSRF Protection ─────────────────────────────────────────────────────────
# SECURITY: CSRF tokens required on all state-changing requests — OWASP A01
CSRF_COOKIE_HTTPONLY         = True
CSRF_COOKIE_SAMESITE         = 'Lax'
CSRF_COOKIE_SECURE           = config('CSRF_COOKIE_SECURE', default=False, cast=bool)

# ─── Security Headers ────────────────────────────────────────────────────────
# SECURITY: Clickjacking protection
X_FRAME_OPTIONS              = 'DENY'

# SECURITY: MIME-type sniffing prevention
SECURE_CONTENT_TYPE_NOSNIFF  = True

# SECURITY: XSS browser protection header
SECURE_BROWSER_XSS_FILTER    = True

# SECURITY: HSTS (enable in production with valid HTTPS)
SECURE_SSL_REDIRECT          = config('SECURE_SSL_REDIRECT', default=False, cast=bool)
SECURE_HSTS_SECONDS          = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD          = True

# ─── Content Security Policy ─────────────────────────────────────────────────
# SECURITY: Restrict resource origins — OWASP A05
CSP_DEFAULT_SRC   = ("'self'",)
CSP_SCRIPT_SRC    = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
CSP_STYLE_SRC     = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net",
                      "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com")
CSP_FONT_SRC      = ("'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com")
CSP_IMG_SRC       = ("'self'", "data:")
CSP_FRAME_ANCESTORS = ("'none'",)

# ─── Brute Force Protection (django-axes) ────────────────────────────────────
# SECURITY: Lock out after 5 failed logins — OWASP A07
AXES_FAILURE_LIMIT           = 5
AXES_COOLOFF_TIME            = 1          # Hours to lock out
AXES_LOCKOUT_TEMPLATE        = 'errors/lockout.html'
AXES_RESET_ON_SUCCESS        = True

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ─── REST Framework ───────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '200/hour',
    },
}

# ─── File Uploads ─────────────────────────────────────────────────────────────
# SECURITY: Limit upload size — OWASP A04
MEDIA_URL    = '/media/'
MEDIA_ROOT   = BASE_DIR / config('MEDIA_ROOT', default='media')
FILE_UPLOAD_MAX_MEMORY_SIZE  = 2 * 1024 * 1024   # 2 MB
DATA_UPLOAD_MAX_MEMORY_SIZE  = 2 * 1024 * 1024

# Allowed image extensions and MIME types (validated in forms too)
ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
ALLOWED_IMAGE_MIMES      = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']

# ─── Static Files ─────────────────────────────────────────────────────────────
STATIC_URL      = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT     = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ─── Auth URLs ────────────────────────────────────────────────────────────────
LOGIN_URL        = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ─── Logging ─────────────────────────────────────────────────────────────────
# SECURITY: Log security events, never log passwords/tokens — OWASP A09
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'securetask.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'securetask.security': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'axes': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Create logs directory if it doesn't exist
(BASE_DIR / 'logs').mkdir(exist_ok=True)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kuala_Lumpur'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
