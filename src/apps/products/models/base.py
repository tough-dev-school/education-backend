from decimal import Decimal
from typing import TYPE_CHECKING

from django.apps import apps
from django.utils.translation import gettext_lazy as _

from apps.studying import shipment_factory as ShipmentFactory
from apps.users.models import User
from core.models import models
from core.models import TimestampedModel
from core.pricing import format_old_price
from core.pricing import format_price

if TYPE_CHECKING:
    from apps.orders.models import Order


class Shippable(TimestampedModel):
    """Add this to every shippable item"""

    name = models.CharField(max_length=255)
    name_receipt = models.CharField(
        _("Name for receipts"), max_length=255, help_text="«посещение мастер-класса по TDD» или «Доступ к записи курсов кройки и шитья»"
    )
    full_name = models.CharField(
        _("Full name for letters"),
        max_length=255,
        help_text="Билет на мастер-класс о TDD или «запись курсов кройки и шитья»",
    )
    name_international = models.CharField(_("Name used for international purchases"), max_length=255, blank=True, default="")

    slug = models.SlugField(unique=True)

    price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    tinkoff_credit_promo_code = models.CharField(
        _("Fixed promo code for tinkoff credit"), max_length=64, blank=True, help_text=_("Used in tinkoff credit only")
    )

    group = models.ForeignKey("products.Group", verbose_name=_("Analytical group"), on_delete=models.PROTECT)

    class Meta:
        abstract = True

    def get_price_display(self) -> str:
        return format_price(self.price)

    def get_old_price_display(self) -> str:
        return format_price(self.old_price)

    def get_formatted_price_display(self) -> str:
        return format_old_price(self.old_price, self.price)

    def ship(self, to: User, order: "Order") -> None:
        return ShipmentFactory.ship(self, to=to, order=order)

    def unship(self, order: "Order") -> None:
        return ShipmentFactory.unship(order=order)

    def get_price(self, promocode: str | None = None) -> Decimal:
        promocode_obj = apps.get_model("orders.PromoCode").objects.get_or_nothing(name=promocode)

        if promocode_obj is not None:
            return promocode_obj.apply(self)

        return self.price

    def get_template_id(self) -> str | None:
        """Get custom per-item template_id"""
        if not hasattr(self, "template_id"):
            return None

        if self.template_id is not None and len(self.template_id):
            return self.template_id
