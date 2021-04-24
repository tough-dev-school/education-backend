from datetime import timedelta

from app.conf.environ import env

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(days=14),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=21),
    'JWT_ALLOW_REFRESH': True,
}
DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS = env('DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS', cast=bool, default=False)
