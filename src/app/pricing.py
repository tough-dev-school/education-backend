from decimal import Decimal

from babel.numbers import format_decimal


def format_price(price: Decimal) -> str:
    if price is not None and price:
        return format_decimal(price, locale='ru_RU')

    return '0'
