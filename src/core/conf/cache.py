from core.conf.environ import env

if env("NO_CACHE", cast=bool, default=False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    }
else:
    CACHES = {
        "default": env.cache("REDISCLOUD_URL"),
    }
