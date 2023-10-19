from app.exceptions import AppServiceException


class AmoCRMException(Exception):
    """Base exceptions for AmoCRM"""


class AmoCRMCacheException(AmoCRMException):
    """Raises when it's impossible to retrieve cached value"""


class AmoCRMServiceException(AppServiceException, AmoCRMException):
    """Base service exception for AmoCRM"""


__all__ = [
    "AmoCRMCacheException",
    "AmoCRMServiceException",
    "AmoCRMException",
]
