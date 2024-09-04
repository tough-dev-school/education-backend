from core.conf.environ import env

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # 'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.auth.middleware.RemoteUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "core.middleware.real_ip.real_ip_middleware",
    "core.middleware.set_user_from_non_django_authentication.JWTAuthMiddleware",
    "core.middleware.set_user_from_non_django_authentication.TokenAuthMiddleware",
    "core.middleware.country.CountryMiddleware",
    "core.middleware.global_current_user.set_global_user",
    "core.middleware.global_request.set_global_request",
    "axes.middleware.AxesMiddleware",
]

if not env("DEBUG") and not env("CI", cast=bool, default=False):
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
