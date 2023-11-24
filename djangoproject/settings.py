from .settings_local import *
import logging.config
from corsheaders.defaults import default_headers
import os
from datetime import timedelta
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
INVEST_ENABLED = False

print('BASE_DIR', BASE_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9jgy5x^c4k2^@j%$^um@s-!tw37*npj7-%(048pvno65!a-y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',

    'blog.apps.BlogConfig',
    'account.apps.AccountConfig',
    'reports.apps.ReportsConfig',
    'api_property.apps.ApiPropertyConfig',
    'rent_analyzer.apps.RentAnalyzerConfig',
    'search.apps.SearchConfig',
    'common.apps.CommonConfig',
    # 'common',

    'ofirio_common.apps.OfirioCommonConfig',

    'crispy_forms',
    'widget_tweaks',
    'ckeditor',
    'ckeditor_uploader',
    'corsheaders',
    'drf_recaptcha',
]
DATABASE_ROUTERS = ('search.dbrouters.DBRouter',
                    'api_property.dbrouters.DBRouter')

DRF_RECAPTCHA_SECRET_KEY = 'secret'
DRF_RECAPTCHA_ACTION_V3_SCORES = {
    "contact_agent_request": 0.6, "contact_us_request": 0.6}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MIDDLEWARE = [
    # 'corsheaders.middleware.CorsPostCsrfMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'djangoproject.middleware.JwtAuthenticationMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    # we still need it bcz of admin forms!
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "account.authentication.SessionAuthentication",
    ),
}

ROOT_URLCONF = 'djangoproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoproject.wsgi.application'


AUTHENTICATION_BACKENDS = [
    'account.authentication.GoogleJwtBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SIMPLE_JWT = {
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'USER_ID_CLAIM': 'email',
    'USER_ID_FIELD': 'email',
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_NAME': 'HTTP_OFAUTH',
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 6}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'account.CustomUser'
LOGIN_REDIRECT_URL = '/api/'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

PROJECT_NAME = 'Ofirio'
PROJECT_SCHEME = 'http://'
PROJECT_DOMAIN = 'localhost:8006'
PROJECT_BACK_EMAIL = 'Ofirio <andrew@rigelstorm.com>'
HELP_EMAIL = 'help@ofirio.com'
INTERCOM_TOKEN = ''
INTERCOM_ENABLED = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

RENT_ANALYZER_CALCULATION_MODEL = 'rent_analyzer.common.rent_analyzer_model.RealRentAnalyzerCalculation'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'tmp/emails')
EMAIL_STATIC_PATH = BASE_DIR / 'djangoproject' / 'static' / 'email'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
SITEMAPS_DIR_SRP = BASE_DIR / 'static_django' / 'sitemaps-srp'

# Cookie
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
COOKIE_SECRET = ''  # Need to be filled in settings_local

# CORS
CORS_ALLOW_HEADERS = list(default_headers) + ['ofauth']


BLUR_IMAGES_QTY = 100  # count of blurred images for search

TEST_RUNNER = 'djangoproject.test_runners.PortalTestRunner'

# Klaviyo
KLAVIYO_API_KEY = ''
KLAVIYO_PRIVATE_KEY = ''
# ID of the Klaviyo list named "Newsletter"
KLAVIYO_NEWSLETTER_LIST_ID = ''
KLAVIYO_ALERTS_RENT_LIST_ID = ''
KLAVIYO_ALERTS_SALE_LIST_ID = ''
KLAVIYO_URL = 'https://a.klaviyo.com/'
# set to False to stop tracking users
KLAVIYO_ENABLED = True

PDF_BACKEND = 'common.pdf.mock_generate_pdf'

CONVERT_IMG_TO_CDN = False
CDN_CONVERSIONS = {
    'listing-images.homejunction.com': 'ofirio-prop-images-s.b-cdn.net',
    'ofirio-prop-images.s3.amazonaws.com': 'ofirio-prop-images.b-cdn.net',
}

IS_PRODUCTION = False

# WordPress
WP_CLIENT_CLASS = 'blog.wp_client.RequestsWordPressClient'
WP_INTERNAL_URL = 'http://localhost'
WP_API_HOST = 'rsprjblog.ofirio.com'
WP_AUTH_USERNAME = ''
WP_AUTH_PASSWORD = ''


JWT_REFRESH_SAMESITE = None


LOG_PATH = BASE_DIR / 'logs'
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "WARNING",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'django.log',
            "formatter": "app",
        },
        "rent_analyzer_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'rent-analyzer.log',
            "formatter": "detailed_fmt",
        },
        "sale_estimator_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'sale-estimator.log',
            "formatter": "detailed_fmt",
        },
        "recommendations_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'recommendations.log',
            "formatter": "detailed_fmt",
        },
        "klaviyo_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'klaviyo.log',
            "formatter": "timestamp_fmt",
        },
        "emails_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'emails.log',
            "formatter": "timestamp_fmt",
        },
        "payments_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'payments.log',
            "formatter": "timestamp_place_fmt",
        },
        "cache_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            'filename': LOG_PATH / 'cache.log',
            "formatter": "timestamp_place_fmt",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False
        },
        "rent_analyzer": {
            "handlers": ["rent_analyzer_file"],
            "level": "INFO",
            "propagate": True
        },
        "sale_estimator": {
            "handlers": ["sale_estimator_file"],
            "level": "INFO",
            "propagate": True
        },
        "recommendations": {
            "handlers": ["recommendations_file"],
            "level": "INFO",
            "propagate": True
        },
        "klaviyo": {
            "handlers": ["klaviyo_file"],
            "level": "INFO",
            "propagate": True
        },
        "emails": {
            "handlers": ["emails_file"],
            "level": "INFO",
            "propagate": True
        },
        "payments": {
            "handlers": ["payments_file"],
            "level": "INFO",
            "propagate": True
        },
        "cache": {
            "handlers": ["cache_file"],
            "level": "INFO",
            "propagate": True
        },
    },
    "formatters": {
        "app": {
            "format": (
                u"%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed_fmt": {
            "format": (
                u"%(asctime)s pid:%(process)d [%(levelname)-8s] "
                "(%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "timestamp_fmt": {
            "format": (
                "%(asctime)s - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "timestamp_place_fmt": {
            "format": (
                "%(asctime)s (%(module)s.%(funcName)s) - %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}
logging.config.dictConfig(LOGGING)

CSRF_TRUSTED_ORIGINS = ['https://localhost', 'https://localhost:8080']
CORS_ORIGIN_ALLOW_ALL = True

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)


# STATIC_URL = "static/"

# STATICFILES_DIRS = [
#     BASE_DIR / "djangoproject/static",
# ]

# STATIC_ROOT = f"{BASE_DIR}/static",
