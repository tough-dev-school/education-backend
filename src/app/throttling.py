from django.conf import settings


class ConfigurableThrottlingMixin:
    def allow_request(self, *args, **kwargs):
        if settings.DISABLE_THROTTLING:
            return True

        return super().allow_request(*args, **kwargs)
