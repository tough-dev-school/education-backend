from datetime import timedelta

from app.conf.environ import env

AUTH_USER_MODEL = 'users.User'

AXES_ENABLED = env('AXES_ENABLED', cast=bool, default=True)

AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': timedelta(days=14),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=21),
    'JWT_ALLOW_REFRESH': True,
    'JWT_ISSUER': 'education-backend',
    'JWT_ALGORITHM': 'RS256',
    'JWT_PRIVATE_KEY': env.str('JWT_PRIVATE_KEY', multiline=True),
    'JWT_PUBLIC_KEY': env.str('JWT_PUBLIC_KEY', multiline=True),
}

DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS = env('DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS', cast=bool, default=False)
