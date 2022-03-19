from app.conf.environ import env

if not env('NO_CACHE', cast=bool, default=False):
    CACHES = {
        'default': env.cache('REDISCLOUD_URL'),
    }

CACHALOT_UNCACHABLE_TABLES = [
    'django_migrations',
    'django_content_type',
    'orders_order',  # https://github.com/noripyt/django-cachalot/issues/126
    'chains_progress',
]
