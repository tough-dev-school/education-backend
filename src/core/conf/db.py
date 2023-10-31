from core.conf.environ import env

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
    "default": env.db(),  # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"  # https://docs.djangoproject.com/en/3.2/releases/3.2/#customizing-type-of-auto-created-primary-keys

if not env("DEBUG", cast=bool):
    DATABASES["default"]["CONN_MAX_AGE"] = 600
