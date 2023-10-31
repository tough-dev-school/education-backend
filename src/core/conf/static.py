import os.path

from core.conf.boilerplate import BASE_DIR
from core.conf.environ import env

STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
