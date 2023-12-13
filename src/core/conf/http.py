from core.conf.environ import env

ABSOLUTE_HOST = env("ABSOLUTE_HOST", cast=str, default="https://app.tough-dev.school")
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://app.tough-dev.school",
]
CORS_ALLOWED_ORIGINS = [
    "https://education.borshev.com",
    "https://tough-dev.school",
    "https://certificates.tough-dev.school",
    "https://lms.tough-dev.school",
]

FRONTEND_URL = env("FRONTEND_URL", cast=str, default="https://lms.tough-dev.school/")
DIPLOMA_FRONTEND_URL = env("DIPLOMA_FRONTEND_URL", cast=str, default="https://cert.tough-dev.school/")

HTTP_CACHE_REDIS_URL = env("REDISCLOUD_URL", cast=str, default="")
