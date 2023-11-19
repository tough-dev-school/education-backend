import sentry_sdk
from rest_framework.response import Response
from rest_framework.views import exception_handler


class AppServiceException(Exception):
    """Inherit your custom service exceptions from this class."""


def app_service_exception_handler(exc: Exception, context: dict) -> Response | None:
    """
    Transform service errors to standard 400 errors and
    Log all DRF exceptions to sentry, including ValidationErrors
    """

    sentry_sdk.capture_exception(exc)

    if not isinstance(exc, AppServiceException):
        return exception_handler(exc, context)

    return Response(status=400, data={"serviceError": str(exc)})
