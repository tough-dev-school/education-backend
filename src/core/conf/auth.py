from datetime import timedelta
from os import path

from core.conf.environ import env

AUTH_USER_MODEL = "users.User"

AXES_ENABLED = env("AXES_ENABLED", cast=bool, default=True)

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesBackend",
    "django.contrib.auth.backends.ModelBackend",
    "django.contrib.auth.backends.RemoteUserBackend",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

keys = {
    "public": env.str("JWT_PUBLIC_KEY", multiline=True),
    "private": env.str("JWT_PRIVATE_KEY", multiline=True),
}

if not keys["public"]:
    with open(path.join(path.dirname(__file__), "/public.pem"), "rb") as fp:
        keys["public"] = fp.read()

if not keys["private"]:
    with open(path.join(path.dirname(__file__), "/private.pem"), "rb") as fp:
        keys["private"] = fp.read()


JWT_AUTH = {
    "JWT_EXPIRATION_DELTA": timedelta(days=14),
    "JWT_REFRESH_EXPIRATION_DELTA": timedelta(days=21),
    "JWT_ALLOW_REFRESH": True,
    "JWT_ISSUER": "education-backend",
    "JWT_ALGORITHM": "RS256",
    "JWT_PRIVATE_KEY": keys["private"],
    "JWT_PUBLIC_KEY": keys["public"],
    "JWT_PAYLOAD_HANDLER": "apps.a12n.jwt.payload_handler",
}

DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS = env("DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS", cast=bool, default=False)
