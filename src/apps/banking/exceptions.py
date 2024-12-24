class BankException(Exception):
    """Base exceptions for Bank errors."""


class BankDoesNotExist(BankException):
    """Bank with given id does not exist."""


class CurrencyRateDoesNotExist(BankException):
    """Currency rate with given name does not exist."""
