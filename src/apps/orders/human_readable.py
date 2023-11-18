from django.utils.html import format_html
from django.utils.translation import gettext as _

from apps.banking.selector import BANK_KEYS
from apps.banking.selector import get_bank
from apps.orders.models import Order


def get_order_payment_method_name(order: Order) -> str:
    """Return the human-readable name of the order payment method."""
    if order.paid is not None:
        if order.bank_id and order.bank_id in BANK_KEYS:
            return str(get_bank(order.bank_id).name)  # type: ignore [union-attr]
        if order.is_b2b:
            return _("B2B")

        return _("Is paid")

    if order.shipped is not None:
        return _("Shipped without payment")

    return "—"


def get_order_customer(order: Order) -> str:
    """Return order's customer in a human-friendly way."""
    name_template = '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;'
    name = str(order.user)
    email = order.user.email

    total_length = len(name) + len(email)

    if total_length < 30:
        return format_html(
            name_template,
            name=name,
            email=email,
        )
    elif 30 <= total_length <= 34:
        return format_html(
            name_template,
            name=order.user.first_name,
            email=email,
        )

    return format_html(
        '<a href="mailto:{email}">{email}</a>',
        email=email,
    )
