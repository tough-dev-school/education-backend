from django.utils.html import format_html

from banking.selector import get_bank
from orders.models.order import Order


class HumanReadableOrder(Order):
    """Order proxy model with methods to display data in a human-friendly way. Methods should not change the data."""

    @property
    def readable_payment_method_name(self) -> str:
        if self.paid is not None:
            if self.bank_id:
                return get_bank(self.bank_id).name
            if self.is_b2b:
                return "B2B"

            return "Is paid"

        if self.shipped is not None:
            return "Shipped without payment"

        return "—"

    @property
    def readable_customer(self) -> str:
        name_template = '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;'
        name = str(self.user)
        email = self.user.email

        total_length = len(name) + len(email)

        if 30 <= total_length <= 34:
            return format_html(
                name_template,
                name=self.user.first_name,
                email=email,
            )
        elif total_length > 34:
            return format_html(
                '<a href="mailto:{email}">{email}</a>',
                email=email,
            )
        else:
            return format_html(
                '{name} &lt;<a href="mailto:{email}">{email}</a>&gt;',
                name=name,
                email=email,
            )

    class Meta:
        proxy = True
