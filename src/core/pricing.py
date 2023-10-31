from decimal import Decimal

from babel.numbers import format_decimal


def format_price(price: Decimal | None) -> str:
    if price is not None and price:
        return format_decimal(price, locale="ru_RU")

    return "0"


def format_old_price(old_price: Decimal | None, new_price: Decimal | None) -> str:
    formatted_new_price = format_price(new_price)
    formatted_old_price = format_price(old_price)

    if formatted_old_price == "0":
        return f"{formatted_new_price} ₽"

    formatted_old_price = "".join([f"{digit}\u0336" for digit in formatted_old_price])
    formatted_old_price = formatted_old_price.replace("\xa0\u0336", "")

    return f"{formatted_old_price} {formatted_new_price} ₽"
