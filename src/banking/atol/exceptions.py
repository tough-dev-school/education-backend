class AtolException(BaseException):
    ...


class AtolAuthError(AtolException):
    ...


__all__ = [
    'AtolException',
    'AtolAuthError',
]
