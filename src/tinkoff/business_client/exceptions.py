class TinkoffBusinessException(Exception):
    pass


class TinkoffBusinessHTTPException(TinkoffBusinessException):
    pass


class TinkoffBusinessClientException(TinkoffBusinessException):
    pass
