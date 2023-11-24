PROJECT_NAME = 'Ofirio'
PROJECT_SCHEME = 'https://'
PROJECT_DOMAIN = 'portal.ofirio.com'
PROJECT_BACK_EMAIL = 'Ofirio <info@ofirio.com>'
HELP_EMAIL = 'help@ofirio.com'
INTERCOM_TOKEN = ''
INTERCOM_ENABLED = True
LOCAL_FRONTEND_PORT = 3000

ALLOWED_HOSTS = ['*']

DEBUG = True

from pathlib import Path
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

STATIC_ROOT = str(BASE_DIR) + '/static'
STATIC_URL = '/static/'
MEDIA_ROOT = str(BASE_DIR) + '/media/'
MEDIA_URL = '/media/'

# It is used to encrypt 'access' cookie.
# Change it when copying the file to settings_local!
COOKIE_SECRET = 'k7cenXveS]@j$*Dl&e[Eg]nT<y$5(B]u'

CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = ''
CKEDITOR_IMAGE_BACKEND = 'pillow'
CKEDITOR_BROWSE_SHOW_DIRS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'email-smtp.eu-west-1.amazonaws.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = '-'
EMAIL_HOST_PASSWORD = '-'
EMAIL_USE_TLS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'prop_db': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'prop_db',
        'USER': 'prop_db',
        'PASSWORD': '102030',
        'HOST': 'localhost',
        'PORT': '5432',
    },
}

# If you want to use local Redis as a cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
#DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

AWS_STORAGE_BUCKET_NAME = 'ofirio-reports-dev'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_QUERYSTRING_AUTH = False
AWS_DEFAULT_ACL = 'public-read'

SOCIAL_AUTH_FACEBOOK_KEY = '-'
SOCIAL_AUTH_FACEBOOK_SECRET = '-'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '-'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '-'

STRIPE_HTTP_CLIENT = 'stripe.http_client.RequestsClient'
STRIPE_PUBLISHABLE_KEY = '-'
STRIPE_SECRET_KEY = '-'
STRIPE_WEBHOOK_ID = ''
STRIPE_WEBHOOK_SECRET = '-'
STRIPE_PREMIUM_PLAN_MONTH = '-'
STRIPE_PREMIUM_PLAN_QUARTER = '-'
STRIPE_PREMIUM_PLAN_YEAR = '-'

GOOGLE_MAPS_API_KEY = ''

# Calculation class to use in Rent Analyzer view and report
RENT_ANALYZER_CALCULATION_MODEL = 'rent_analyzer.views.rent_analyzer_model.RealRentAnalyzerCalculation'

PDF_BACKEND = 'common.pdf.real_generate_pdf'  # or 'common.pdf.mock_generate_pdf'

CONVERT_IMG_TO_CDN = True

DEV_LOGO_NAME = ''

ELASTICSEARCH_URL = ''
ELASTICSEARCH_PORT = 9200

SLACK_WEBHOOK_URL = ''

RUNTIME_CHECKS = [
    # 'ofirio_common.runtime_check.CeleryCheck',
]
RUNTIME_CHECK_EMAILS = [
    # 'team.member@rigelstorm.com',
]

TG_BOT_TOKEN = ''
TG_INTERNAL_CHANNEL_ID = ''

#ONLY FOR TEST PURPOSES
#CORS_ALLOW_ALL_ORIGINS = False
#CORS_ALLOWED_ORIGINS = [
#        'http://localhost:8080',
#        'https://localhost:8080',
#]
#CORS_ALLOW_CREDENTIALS = True
#CSRF_TRUSTED_ORIGINS = [
#    'localhost:8080',
#]

#ONLY FOR TEST PURPOSES
#CSRF_COOKIE_SAMESITE = 'None'
#SESSION_COOKIE_SAMESITE = 'None'

# Klaviyo
KLAVIYO_API_KEY = ''
KLAVIYO_PRIVATE_KEY = ''
# ID of the Klaviyo list named "Newsletter"
KLAVIYO_NEWSLETTER_LIST_ID = ''
KLAVIYO_URL = 'https://a.klaviyo.com/'
# set to False to stop tracking users
KLAVIYO_ENABLED = True

CELERY_TASK_ALWAYS_EAGER = False
CELERY_BROKER_URL = 'amqp://localhost:5672/portal'

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# sentry_sdk.init(
#     dsn="-",
#     integrations=[DjangoIntegration()],

#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,

#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     send_default_pii=True
# )
# # bind to remote socket locally:
# # ssh ubuntu@${portal_ip} -L ~/socket.sock:/home/ubuntu/portal_next_dev/searchseourlgenerator.sock -N -v
# URLGEN_SOCKET_ADDRESS = '/home/user/socket.sock'
