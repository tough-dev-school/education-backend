import os.path

from app.conf.boilerplate import BASE_DIR
from app.conf.environ import env

STATIC_URL = env("STATIC_URL", default="/static/")
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
