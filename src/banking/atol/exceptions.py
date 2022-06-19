class AtolException(BaseException):
    ...


class AtolAuthError(AtolException):
    ...


class AtolHTTPError(AtolException):
    ...


__all__ = [
    'AtolException',
    'AtolAuthError',
]
