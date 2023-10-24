from decimal import Decimal
from typing import Callable

import stripe

from stripebank.bank import StripeBank

STRIPE_EVENT_HANDLERS: dict[str, Callable[[stripe.Event], None]] = {}


def default_handler(webhook_event: stripe.Event) -> None:
    pass


def register(event: str) -> Callable[[Callable[[stripe.Event], None]], None]:
    def decorator(handler: Callable[[stripe.Event], None]) -> None:
        STRIPE_EVENT_HANDLERS[event] = handler

    return decorator


def get(event: str) -> Callable[[stripe.Event], None]:
    return STRIPE_EVENT_HANDLERS.get(event, default_handler)


def convert_amount(stripe_amount: int) -> Decimal:
    return Decimal(stripe_amount / 100 * StripeBank.ue)


__all__ = [
    "register",
    "get",
    "convert_amount",
]
