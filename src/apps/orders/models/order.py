from typing import Iterable

import shortuuid

from django.db.models import CheckConstraint
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.banking.selector import BANK_CHOICES
from apps.orders.exceptions import UnknownItemException
from apps.orders.fields import ItemField
from apps.products.models import Product
from core.models import models
from core.models import only_one_or_zero_is_set
from core.models import TimestampedModel


class OrderQuerySet(QuerySet):
    def paid(self, invert: bool | None = False) -> "OrderQuerySet":
        return self.filter(paid__isnull=invert)

    def shipped_without_payment(self) -> "OrderQuerySet":
        return self.paid(invert=True).filter(shipped__isnull=False)

    def available_to_confirm(self) -> "OrderQuerySet":
        return self.filter(
            price=0,
        )

    def same_deal(self, order: "Order") -> "OrderQuerySet":
        return self.filter(user=order.user, course=order.course).exclude(pk=order.pk)


OrderManager = models.Manager.from_queryset(OrderQuerySet)


class Order(TimestampedModel):
    objects = OrderManager()

    slug = models.CharField(max_length=32, db_index=True, unique=True, default=shortuuid.uuid)

    author = models.ForeignKey("users.User", related_name="created_orders", verbose_name=_("Order author"), on_delete=models.PROTECT, editable=False)
    user = models.ForeignKey("users.Student", verbose_name=_("User"), on_delete=models.PROTECT)
    price = models.DecimalField(_("Price"), max_digits=9, decimal_places=2)
    promocode = models.ForeignKey("orders.PromoCode", verbose_name=_("Promo Code"), blank=True, null=True, on_delete=models.PROTECT)

    paid = models.DateTimeField(
        _("Date when order got paid"),
        null=True,
        blank=True,
    )
    unpaid = models.DateTimeField(_("Date when order got unpaid"), null=True, blank=True)
    shipped = models.DateTimeField(_("Date when order was shipped"), null=True, blank=True)

    bank_id = models.CharField(_("User-requested bank string"), choices=BANK_CHOICES, blank=True, max_length=32)
    ue_rate = models.IntegerField(_("Purchase-time UE rate"))
    acquiring_percent = models.DecimalField(default=0, max_digits=4, decimal_places=2)

    course = ItemField(to="products.Course", verbose_name=_("Course"), null=True, blank=True, on_delete=models.PROTECT)
    record = ItemField(to="products.Record", verbose_name=_("Record"), null=True, blank=True, on_delete=models.PROTECT)
    bundle = ItemField(to="products.Bundle", verbose_name=_("Bundle"), null=True, blank=True, on_delete=models.PROTECT)

    amocrm_lead = models.OneToOneField("amocrm.AmoCRMOrderLead", on_delete=models.SET_NULL, null=True, blank=True, related_name="order")
    amocrm_transaction = models.OneToOneField("amocrm.AmoCRMOrderTransaction", on_delete=models.SET_NULL, null=True, blank=True, related_name="order")

    analytics = models.JSONField(default=dict)

    class Meta:
        ordering = ["-id"]
        verbose_name = pgettext_lazy("orders", "Order")
        verbose_name_plural = pgettext_lazy("orders", "Orders")

        permissions = [
            ("pay_order", _("May mark orders as paid")),
            ("unpay_order", _("May mark orders as unpaid")),
        ]

        constraints = [
            CheckConstraint(
                check=only_one_or_zero_is_set("course", "record", "bundle"),
                name="only_one_or_zero_item_type_is_allowed",
            ),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk}--{self.slug}"

    @property
    def is_b2b(self) -> bool:
        return self.author_id != self.user_id

    @property
    def item(self) -> Product:  # type: ignore
        """Find the attached item. Simple replacement for ContentType framework"""
        for field in self.__class__._meta.get_fields():
            if getattr(field, "_is_item", False):
                if getattr(self, f"{field.name}_id", None) is not None:
                    return getattr(self, field.name)

    @classmethod
    def _iterate_items(cls) -> Iterable[models.fields.Field]:
        for field in cls._meta.get_fields():
            if getattr(field, "_is_item", False):
                yield field  # type: ignore

    @classmethod
    def get_item_foreignkey(cls, item: Product) -> str | None:
        """
        Given an item model, returns the ForeignKey to it"""
        for field in cls._iterate_items():
            if field.related_model == item.__class__:
                return field.name

    def reset_items(self) -> None:
        for field in self._iterate_items():
            setattr(self, field.name, None)

    def set_item(self, item: Product) -> None:
        if self.shipped is not None:  # some denormalization happens during shipping, so please do not break it!
            raise ValueError("Cannot change item for shipped order!")

        foreign_key = self.__class__.get_item_foreignkey(item)
        if foreign_key is not None:
            self.reset_items()
            setattr(self, foreign_key, item)
            return

        raise UnknownItemException(f"There is no foreignKey for {item.__class__}")

    def set_paid(self, silent: bool | None = False) -> None:
        from apps.orders.services import OrderPaidSetter

        OrderPaidSetter(self, silent=silent)()

    def refund(self) -> None:
        from apps.orders.services import OrderRefunder

        OrderRefunder(self)()

    def ship(self, silent: bool | None = False) -> None:
        from apps.orders.services import OrderShipper

        OrderShipper(self, silent=silent)()

    def ship_without_payment(self) -> bool:
        if self.paid is None:
            self.ship(silent=True)
            return True

        return False

    def unship(self) -> None:
        from apps.orders.services import OrderUnshipper

        OrderUnshipper(self)()
