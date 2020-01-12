from decimal import Decimal

from babel.numbers import format_decimal


def format_price(price: Decimal) -> str:
    if price is not None and price:
        return format_decimal(price, locale='ru_RU')

    return '0'


def format_old_price(old_price: Decimal, price: Decimal) -> str:
    price = format_price(price)
    old_price = format_price(old_price)

    if old_price == '0':
        return f'{price} ₽'

    old_price = ''.join([f'{digit}\u0336' for digit in old_price])
    old_price = old_price.replace('\xa0\u0336', '')

    return f'{old_price} {price} ₽'
