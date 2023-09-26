from split_settings.tools import include

from app.conf.environ import env

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", cast=str, default="s3cr3t")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG", cast=bool, default=False)
CI = env("CI", cast=bool, default=False)

# Application definition

include(
    "conf/api.py",
    "conf/auth.py",
    "conf/boilerplate.py",
    "conf/cache.py",
    "conf/db.py",
    "conf/debug_toolbar.py",
    "conf/email.py",
    "conf/features.py",
    "conf/healthchecks.py",
    "conf/http.py",
    "conf/i18n.py",
    "conf/installed_apps.py",
    "conf/markdown.py",
    "conf/media.py",
    "conf/middleware.py",
    "conf/sentry.py",
    "conf/storage.py",
    "conf/static.py",
    "conf/warnings.py",
    "conf/templates.py",
    "conf/timezone.py",
    "conf/vat.py",
    "conf/tags.py",
)

include("conf/integrations/*.py")
include("conf/integrations/banking/*.py")
