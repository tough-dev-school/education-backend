from core.conf.environ import env

USE_TZ = True

TIME_ZONE = env("TIME_ZONE", cast=str, default="Europe/Moscow")
