from core.conf.environ import env

DEBUG = env("DEBUG", cast=bool, default=False)

DISABLE_HOMEWORK_PERMISSIONS_CHECKING = env("DISABLE_HOMEWORK_PERMISSIONS_CHECKING", cast=bool, default=DEBUG)

DISABLE_NEW_ANSWER_NOTIFICATIONS = env("DISABLE_NEW_ANSWER_NOTIFICATIONS", cast=bool, default=False)
