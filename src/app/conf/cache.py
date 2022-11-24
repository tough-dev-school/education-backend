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

if env('CI', cast=bool, default=False):
    CACHALOT_ENABLED = False  # disable `django-cachalot` in tests https://github.com/noripyt/django-cachalot/issues/126

CACHALOT_UNCACHABLE_TABLES = [
    'django_migrations',
    'django_content_type',
]
