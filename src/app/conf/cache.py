from app.conf.environ import env

NOTION_CACHE = {
    "BACKEND": "django.core.cache.backends.db.DatabaseCache",
    "LOCATION": "notion_cache_table",
}

if env("NO_CACHE", cast=bool, default=False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
        "notion": NOTION_CACHE,
    }
else:
    CACHES = {
        "default": env.cache("REDISCLOUD_URL"),
        "notion": NOTION_CACHE,
    }
