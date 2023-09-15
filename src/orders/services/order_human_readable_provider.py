from django.utils.html import format_html
from django.utils.translation import gettext as _

from banking.selector import get_bank
from orders.models import Order


class OrderHumanReadableProvider:  # noqa: PIE798
    """Methods to provide `Order` in human-friendly form."""

    @staticmethod
    def get_payment_method_name(order: Order) -> str:
        """Return human readable payment method name"""
        if order.paid is not None:
            if order.bank_id:
                return get_bank(order.bank_id).name
            if order.is_b2b:
                return _("B2B")

            return _("Is paid")

        if order.shipped is not None:
            return _("Shipped without payment")

        return "—"

    @staticmethod
    def get_customer(order: Order) -> str:
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
        else:
            return format_html(
                '<a href="mailto:{email}">{email}</a>',
                email=email,
            )
