from datetime import timedelta

from core.conf.environ import env

DEBUG = env("DEBUG", cast=bool, default=False)

DISABLE_NEW_ANSWER_NOTIFICATIONS = env("DISABLE_NEW_ANSWER_NOTIFICATIONS", cast=bool, default=False)

HOMEWORK_ANSWER_EDIT_PERIOD = timedelta(days=1)
