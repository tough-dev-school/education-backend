import environ
import os
import os.path
from celery.schedules import crontab
from datetime import timedelta

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
FRONTEND_URL = env('FRONTEND_URL', cast=str, default='https://education.borshev.com/lms/')

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
    'education-backend.herokuapp.com',
    'edu-app.borshev.com',
    'localhost',
    'localhost:8000',
    'education.borshev.com',
    ABSOLUTE_HOST.replace('https://', ''),
]

CORS_ALLOWED_ORIGINS = [
    'https://education.borshev.com',
]
CORS_ORIGIN_REGEX_WHITELIST = [
    r'.*education-frontend.netlify.app.*',
]

CSRF_TRUSTED_ORIGINS = [
    'education.borshev.com',
    'borshev.com',
    'education-frontend.netlify.app',
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
    'banking',
    'a12n',
    'homework',

    'markdownx',
    'corsheaders',
    'hattori',
    'anymail',
    'rest_framework',
    'rest_framework.authtoken',
    'drf_recaptcha',
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
    'app.middleware.real_ip.real_ip_middleware',
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
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'app.renderers.AppJSONRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PAGINATION_CLASS': 'app.pagination.AppPagination',
    'EXCEPTION_HANDLER': 'app.sentry_exception_handler.sentry_exception_handler',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_RATES': {
        'anon-auth': '10/min',
    },
}
DISABLE_THROTTLING = env('DISABLE_THROTTLING', cast=bool, default=env('DEBUG'))
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(days=14),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=21),
    'JWT_ALLOW_REFRESH': True,
}
DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS = env('DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS', cast=bool, default=False)


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
if not DEBUG:
    DATABASES['default']['CONN_MAX_AGE'] = 600

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

SENTRY_DSN = env('SENTRY_DSN', cast=str, default='')

if not DEBUG and SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
    )

BROKER_URL = env('REDIS_URL')
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


DEFAULT_FILE_STORAGE = env('DEFAULT_FILE_STORAGE', cast=str, default='django.core.files.storage.FileSystemStorage')
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default=None)
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default=None)
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default=None)
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default=None)
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default=None)
AWS_DEFAULT_ACL = env('AWS_DEFAULT_ACL', default='public-read')
AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False


MARKDOWNX_URLS_PATH = '/api/v2/markdownx/markdownify/'
MARKDOWNX_UPLOAD_URLS_PATH = '/api/v2/markdownx/upload/'
MARKDOWNX_MARKDOWNIFY_FUNCTION = 'app.markdown.markdownify'

DISABLE_HOMEWORK_PERMISSIONS_CHECKING = env('DISABLE_HOMEWORK_PERMISSIONS_CHECKING', cast=bool, default=DEBUG)


EMAIL_ENABLED = env('EMAIL_ENABLED', cast=bool, default=False)

EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

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
TINKOFF_CREDIT_SHOP_ID = env('TINKOFF_CREDIT_SHOP_ID', default=None)
TINKOFF_CREDIT_SHOWCASE_ID = env('TINKOFF_CREDIT_SHOWCASE_ID', default=None)

TINKOFF_CREDIT_DEMO_MODE = env('TINKOFF_CREDIT_DEMO_MODE', default=DEBUG)

BOT_TOKEN = env('BOT_TOKEN', cast=str, default=None)
HAPPINESS_MESSAGES_CHAT_ID = env('HAPPINESS_MESSAGES_CHAT_ID', cast=str, default=None)

DRF_RECAPTCHA_SECRET_KEY = env('RECAPTCHA_SECRET_KEY', cast=str, default='')
DRF_RECAPTCHA_TESTING = DRF_RECAPTCHA_TESTING_PASS = not env('RECAPTCHA_ENABLED', cast=bool, default=True)
