from core.conf.environ import env

DISABLE_THROTTLING = env("DISABLE_THROTTLING", cast=bool, default=env("DEBUG"))

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "core.renderers.AppJSONRenderer",
    ],
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_PAGINATION_CLASS": "core.pagination.AppPagination",
    "EXCEPTION_HANDLER": "core.exceptions.app_service_exception_handler",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_RATES": {
        "anon-auth": "10/min",
        "public-id": "60/hour",
        "notion-materials": "100/hour",
        "promocode": "100/hour",
        "purchase": "100/hour",
    },
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
DRF_RECAPTCHA_SECRET_KEY = env("RECAPTCHA_SECRET_KEY", cast=str, default="")
DRF_RECAPTCHA_TESTING = DRF_RECAPTCHA_TESTING_PASS = not env("RECAPTCHA_ENABLED", cast=bool, default=True)

if env("DEBUG"):
    REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"].append("rest_framework.authentication.SessionAuthentication")  # type: ignore

    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].append("rest_framework.renderers.BrowsableAPIRenderer")  # type: ignore


# Set up drf_spectacular, https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "Tough dev school API",
    "DESCRIPTION": "So great, needs no docs",
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
}
