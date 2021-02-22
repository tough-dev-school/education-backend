import sentry_sdk
from rest_framework.views import exception_handler


def sentry_exception_handler(exc, context):
    """Log all DRF exceptions to sentry, including ValidationErrors"""
    sentry_sdk.capture_exception(exc)

    return exception_handler(exc, context)
