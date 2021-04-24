from app.conf.environ import env

DISABLE_THROTTLING = env('DISABLE_THROTTLING', cast=bool, default=env('DEBUG'))

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': [
        'app.renderers.AppJSONRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_PAGINATION_CLASS': 'app.pagination.AppPagination',
    'EXCEPTION_HANDLER': 'app.sentry_exception_handler.sentry_exception_handler',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_RATES': {
        'anon-auth': '10/min',
    },
}
DRF_RECAPTCHA_SECRET_KEY = env('RECAPTCHA_SECRET_KEY', cast=str, default='')
DRF_RECAPTCHA_TESTING = DRF_RECAPTCHA_TESTING_PASS = not env('RECAPTCHA_ENABLED', cast=bool, default=True)
