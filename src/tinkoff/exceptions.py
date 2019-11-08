class TinkoffException(Exception):
    pass


class TinkoffPaymentNotificationInvalidToken(TinkoffException):
    pass


class TinkoffPaymentNotificationNoTokenPassed(TinkoffException):
    pass
