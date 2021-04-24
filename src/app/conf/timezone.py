from app.conf.environ import env

USE_TZ = False

TIME_ZONE = env('TIME_ZONE', cast=str, default='Europe/Moscow')
