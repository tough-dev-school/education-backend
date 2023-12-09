class DashamailException(BaseException):
    """Base dashamail exception"""


class DashamailHTTPException(DashamailException):
    pass


class DashamailWrongResponse(DashamailHTTPException):
    """Wrong response from the lists API"""


class DashamailWrongFrontendAPIResponse(DashamailHTTPException):
    """Wrong response from the frontend API"""


class DashamailSubscriptionFailed(DashamailException):
    pass


class DashamailUpdateFailed(DashamailException):
    pass
