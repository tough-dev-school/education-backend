from app.conf.environ import env

DEBUG = env('DEBUG', cast=bool, default=False)

DISABLE_HOMEWORK_PERMISSIONS_CHECKING = env('DISABLE_HOMEWORK_PERMISSIONS_CHECKING', cast=bool, default=DEBUG)
