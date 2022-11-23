from app.conf.environ import env

CACHES = {
    'default': env.cache('REDISCLOUD_URL'),
}

if env('NO_CACHE', cast=bool, default=False):
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        },
    }

CACHALOT_ENABLED = env('CACHALOT_ENABLED', cast=bool, default=True)
CACHALOT_UNCACHABLE_TABLES = [
    'django_migrations',
    'django_content_type',
    'orders_order',  # https://github.com/noripyt/django-cachalot/issues/126
    'chains_progress',
]
