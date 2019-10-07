import json
import os
import textwrap

import environ
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate

root = environ.Path(__file__) - 2        # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False))  # set default values and casting
environ.Env.read_env()                   # reading .env file
SITE_ROOT = root()

USE_L10N = True
USE_i18N = True

LANGUAGE_CODE = "en"

USE_TZ = True
TIME_ZONE = env('TIME_ZONE', cast=str, default='Europe/Moscow')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEST_RUNNER = 'app.test.disable_test_command_runner.DisableTestCommandRunner'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1v(zv1m7oy1co0c$$q52_i7-yr4g#@z0$y0xh%a=#p%si5n3*l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'auth0',
    'users',

    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',

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
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
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
CACHES = {
    'default': env.cache(),
}
AUTH_USER_MODEL = 'users.User'
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]

with open(os.path.join(SITE_ROOT, 'auth0', 'jwks.json'), 'r') as publickey_file:
    jwks = json.load(publickey_file)
    cert = '-----BEGIN CERTIFICATE-----\n' + textwrap.fill(jwks['keys'][0]['x5c'][0], 64) + '\n-----END CERTIFICATE-----'
    certificate = load_pem_x509_certificate(str.encode(cert), default_backend())
    publickey = certificate.public_key()


JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
        'auth0.user.jwt_get_username_from_payload_handler',
    'JWT_PUBLIC_KEY': publickey,
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': 'weightless.pro/api',
    'JWT_ISSUER': 'https://f213.eu.auth0.com/',
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

MEDIA_URL = env('MEDIA_URL')
MEDIA_ROOT = env('MEDIA_ROOT')

STATIC_URL = env('STATIC_URL')
STATIC_ROOT = env('STATIC_ROOT')

SUIT_CONFIG = {
    'ADMIN_NAME': 'myapp secret place',
}

# Uncomment this lines to catch all runtime warnings as errors

# import warnings  # noqa
# warnings.filterwarnings(
#     'error', r".*",
#     RuntimeWarning, r".*"
# )
