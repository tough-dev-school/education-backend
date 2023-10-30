class DashamailException(BaseException):
    """Base dashamail exception"""


class DashamailHTTPException(DashamailException):
    pass


class DashamailWrongResponse(DashamailHTTPException):
    pass


class DashamailSubscriptionFailed(DashamailException):
    pass


class DashamailUpdateFailed(DashamailException):
    pass
