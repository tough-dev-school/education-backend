from core.conf.environ import env

CLICKMEETING_API_KEY = env("CLICKMEETING_API_KEY", default=None, cast=str)
