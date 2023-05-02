from app.conf.environ import env

NOTION_MIDDLEWARE_URL = env("NOTION_MIDDLEWARE_URL", cast=str, default="")
NOTION_MIDDLEWARE_TIMEOUT = env("NOTION_MIDDLEWARE_TIMEOUT", cast=int, default=15)
