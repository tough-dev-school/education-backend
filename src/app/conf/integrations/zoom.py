from app.conf.environ import env

ZOOMUS_API_KEY = env("ZOOMUS_API_KEY", default=None, cast=str)
ZOOMUS_API_SECRET = env("ZOOMUS_API_SECRET", default=None, cast=str)
