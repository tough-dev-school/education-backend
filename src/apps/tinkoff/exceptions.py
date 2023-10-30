class TinkoffException(Exception):
    pass


class TinkoffRequestException(TinkoffException):
    pass


class TinkoffPaymentNotificationInvalidToken(TinkoffException):
    pass


class TinkoffPaymentNotificationNoTokenPassed(TinkoffException):
    pass
