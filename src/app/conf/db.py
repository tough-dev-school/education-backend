from app.conf.environ import env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    'default': env.db(),    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}

if not env('DEBUG', cast=bool):
    DATABASES['default']['CONN_MAX_AGE'] = 600
