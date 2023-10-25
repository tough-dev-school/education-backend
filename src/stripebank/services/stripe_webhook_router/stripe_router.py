from typing import Callable

import stripe

STRIPE_EVENT_HANDLERS: dict[str, Callable[[stripe.Event], None]] = {}


def default_handler(webhook_event: stripe.Event) -> None:
    pass


def register(event_type: str) -> Callable[[Callable[[stripe.Event], None]], Callable | None]:
    def decorator(handler: Callable[[stripe.Event], None]) -> Callable[[stripe.Event], None]:
        STRIPE_EVENT_HANDLERS[event_type] = handler

        return handler

    return decorator


def get(event_type: str) -> Callable[[stripe.Event], None]:
    return STRIPE_EVENT_HANDLERS.get(event_type, default_handler)


__all__ = [
    "register",
    "get",
]
