import environ
import os
from celery.schedules import crontab

root = environ.Path(__file__) - 2        # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False))  # set default values and casting
environ.Env.read_env()                   # reading .env file
SITE_ROOT = root()

USE_L10N = True
USE_i18N = True

LANGUAGE_CODE = 'ru'
LOCALE_PATHS = ['locale']

INTERNAL_IPS = [
    '127.0.0.1',
]
FRONTEND_URL = 'https://education.borshev.com'

USE_TZ = False
TIME_ZONE = env('TIME_ZONE', cast=str, default='Europe/Moscow')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_RUNNER = 'app.test.disable_test_command_runner.DisableTestCommandRunner'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', cast=str, default='s3cr3t')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', cast=bool, default=False)
CI = env('CI', cast=bool, default=False)
ANONYMIZE_ENABLED = DEBUG

ABSOLUTE_HOST = env('ABSOLUTE_HOST', cast=str, default='https://edu-app.borshev.com')
ALLOWED_HOSTS = [
    'edu-app.borshev.com',
    'localhost',
    'localhost:8000',
    'education.borshev.com',
    ABSOLUTE_HOST.replace('https://', ''),
]

CORS_ORIGIN_WHITELIST = [
    'https://pmdaily.ru',
    'https://education.borshev.com',
]

CSRF_TRUSTED_ORIGINS = [
    'pmdaily.ru',
    'education.borshev.com',
    'borshev.com',
]


# Application definition

INSTALLED_APPS = [
    'app',
    'users',
    'orders',
    'products',
    'shipping',
    'tinkoff',
    'triggers',
    'magnets',

    'corsheaders',
    'hattori',
    'anymail',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

    'axes',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

if not DEBUG and not CI:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'app.renderers.AppJSONRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PAGINATION_CLASS': 'app.pagination.AppPagination',
    'PAGE_SIZE': 20,
}

ROOT_URLCONF = 'app.urls'

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

WSGI_APPLICATION = 'app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': env.db(),    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]
HEALTH_CHECKS_ERROR_CODE = 503
HEALTH_CHECKS = {
    'db': 'django_healthchecks.contrib.check_database',
}

MEDIA_URL = env('MEDIA_URL', default='/media/')

STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = env('STATIC_ROOT')

SENTRY_DSN = env('SENTRY_DSN', cast=str, default='')

if not DEBUG and len(SENTRY_DSN):
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
    )

BROKER_URL = env('CELERY_BACKEND')
CELERY_ALWAYS_EAGER = env('CELERY_ALWAYS_EAGER', cast=bool, default=DEBUG)  # by default in debug mode we run all celery tasks in foregroud.
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = False
CELERYBEAT_SCHEDULE = {
    'run_started_purchase_trigger': {
        'task': 'triggers.tasks.check_for_started_purchase_triggers',
        'schedule': crontab(hour='*', minute=15),
    },
    'run_record_feedback_trigger': {
        'task': 'triggers.tasks.check_for_record_feedback_triggers',
        'schedule': crontab(hour='*', minute=15),
    },
    'ship_unshipped_orders': {
        'task': 'orders.tasks.ship_unshipped_orders',
        'schedule': crontab(hour='*', minute='*/2'),
    },
}


AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=None)
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default=None)
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default=None)

EMAIL_ENABLED = env('EMAIL_ENABLED', cast=bool, default=False)

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

MAILJET_API_KEY = env('MAILJET_API_KEY', default='')
MAILJET_SECRET_KEY = env('MAILJET_SECRET_KEY', default='')
MAILJET_CONTACT_LIST_ID = env('MAILJET_CONTACT_LIST_ID', cast=int, default=None)

MAILCHIMP_API_KEY = env('MAILCHIMP_API_KEY', default='')
MAILCHIMP_CONTACT_LIST_ID = env('MAILCHIMP_CONTACT_LIST_ID', cast=str, default=None)

DEFAULT_FROM_EMAIL = env('EMAIL_FROM', cast=str, default='')
ANYMAIL = {
    'POSTMARK_SERVER_TOKEN': env('POSTMARK_SERVER_TOKEN', cast=str, default=''),
    'DEBUG_API_REQUESTS': env('DEBUG'),
}

CLICKMEETING_API_KEY = env('CLICKMEETING_API_KEY', default=None, cast=str)

ZOOMUS_API_KEY = env('ZOOMUS_API_KEY', default=None, cast=str)
ZOOMUS_API_SECRET = env('ZOOMUS_API_SECRET', default=None, cast=str)

TINKOFF_TERMINAL_KEY = env('TINKOFF_TERMINAL_KEY', default=None)
TINKOFF_TERMINAL_PASSWORD = env('TINKOFF_TERMINAL_PASSWORD', default=None)

SEND_HAPPINESS_MESSAGES = env('SEND_HAPPINESS_MESSAGES', cast=bool, default=False)

# Uncomment this lines to catch all runtime warnings as errors

# import warnings  # noqa
# warnings.filterwarnings(
#     'error', r".*",
#     RuntimeWarning, r".*"
# )
