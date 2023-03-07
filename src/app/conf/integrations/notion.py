from app.conf.environ import env

NOTION_TOKEN = env("NOTION_TOKEN", cast=str, default="")
