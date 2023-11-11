from pathlib import Path


BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

CKEDITOR_UPLOAD_PATH = ''

STRIPE_PREMIUM_PLAN_MONTH = ''
STRIPE_PREMIUM_PLAN_QUARTER = ''
STRIPE_PREMIUM_PLAN_YEAR = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

CELERY_TASK_ALWAYS_EAGER = True

ELASTICSEARCH_URL = ''
ELASTICSEARCH_PORT = 9200

TG_BOT_TOKEN = ''

PDF_BACKEND = 'common.pdf.mock_generate_pdf'
