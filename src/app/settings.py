import os

import environ
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
FRONTEND_URL = 'https://pmdaily.ru'

USE_TZ = False
TIME_ZONE = env('TIME_ZONE', cast=str, default='Europe/Moscow')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_RUNNER = 'app.test.disable_test_command_runner.DisableTestCommandRunner'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tei5ie3Ki4ahra8Dei9gahj9tain;ae7aif6ayahtaephooto=aW]ios6oLo^Nga'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', cast=bool, default=False)
CI = env('CI', cast=bool, default=False)

ALLOWED_HOSTS = [
    'app.pmdaily.ru',
    'localhost',
    'localhost:8000',
    '85c8ac7a.ngrok.io',
]

CSRF_TRUSTED_ORIGINS = [
    'pmdaily.ru',
]


# Application definition

INSTALLED_APPS = [
    'app',
    'users',
    'orders',
    'courses',
    'onetime',
    'shipping',
    'tinkoff',
    'triggers',

    'anymail',
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'rest_framework_tracking',

    'suit',
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
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

if not DEBUG and not CI:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
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

SUIT_CONFIG = {
    'ADMIN_NAME': 'Админка курсов',
    'MENU_ICONS': {
        'courses': 'icon-folder-close',
        'orders': 'icon-shopping-cart',
        'onetime': 'icon-lock',
        'auth': 'icon-lock',
    },
    'MENU_EXCLUDE': [
        'authtoken',
    ],
}

SENTRY_DSN = env('SENTRY_DSN', cast=str, default='')

if not DEBUG and len(SENTRY_DSN):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
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
    'run_record_purchase_trigger': {
        'task': 'triggers.tasks.check_for_record_purchase_triggers',
        'schedule': crontab(hour='*', minute=15),
    },
}

ABSOLUTE_HOST = env('ABSOLUTE_HOST', cast=str, default='https://app.pmdaily.ru')


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

ANYMAIL = {
    'MAILJET_API_KEY': MAILJET_API_KEY,
    'MAILJET_SECRET_KEY': MAILJET_SECRET_KEY,
}

CLICKMEETING_API_KEY = env('CLICKMEETING_API_KEY', default=None, cast=str)

TINKOFF_TERMINAL_KEY = env('TINKOFF_TERMINAL_KEY', default=None)
TINKOFF_TERMINAL_PASSWORD = env('TINKOFF_TERMINAL_PASSWORD', default=None)

SEND_HAPPINESS_MESSAGES = env('SEND_HAPPINESS_MESSAGES', cast=bool, default=False)

# Uncomment this lines to catch all runtime warnings as errors

# import warnings  # noqa
# warnings.filterwarnings(
#     'error', r".*",
#     RuntimeWarning, r".*"
# )
