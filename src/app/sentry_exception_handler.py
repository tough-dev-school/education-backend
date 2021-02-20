from logging import exception
from rest_framework.views import exception_handler
from sentry_sdk import capture_exception


def sentry_exception_handler(exc, context):
    """Log all DRF exceptions to sentry"""
    response = exception_handler(exc, context)

    capture_exception(exception)

    return response
