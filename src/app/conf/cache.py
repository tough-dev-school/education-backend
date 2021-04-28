from app.conf.environ import env

CACHES = {
    'default': env.cache('REDIS_URL'),
}

CACHALOT_UNCACHABLE_TABLES = [
    'django_migrations',
    'django_content_type',
    'orders_order',  # https://github.com/noripyt/django-cachalot/issues/126
]
