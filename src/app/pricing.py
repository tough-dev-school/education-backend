from decimal import Decimal

from babel.numbers import format_decimal

STRIKETHROUGH = {
    '1': '1̶',
    '2': '2̶',
    '3': '3̶',
    '4': '4̶',
    '5': '5̶',
    '6': '6̶',
    '7': '7̶',
    '8': '8̶',
    '9': '9̶',
    '0': '0̶',
    ',': ',̶',
}


def format_price(price: Decimal) -> str:
    if price is not None and price:
        return format_decimal(price, locale='ru_RU')

    return '0'


def format_old_price(old_price: Decimal, price: Decimal) -> str:
    price = format_price(price)
    old_price = format_price(old_price)

    if old_price == '0':
        return f'{price} ₽'

    old_price = ''.join([STRIKETHROUGH.get(digit, digit) for digit in old_price])
    old_price = old_price.replace('\xa0', '')

    return f'{old_price} {price} ₽'
