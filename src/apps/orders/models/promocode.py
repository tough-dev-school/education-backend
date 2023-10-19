import contextlib
from decimal import Decimal
from typing import Optional  # NOQA: I251

from django.core.exceptions import ValidationError
from django.db.models import Case
from django.db.models import CheckConstraint
from django.db.models import Count
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models import When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.products.models import Course
from core.models import models
from core.models import TimestampedModel


class PromoCodeQuerySet(QuerySet):
    def active(self) -> QuerySet["PromoCode"]:
        return self.filter(
            active=True,
        ).filter(
            Q(expires__isnull=True) | Q(expires__gte=timezone.now()),
        )

    def with_order_count(self) -> QuerySet["PromoCode"]:
        return self.annotate(
            order_count=Count(
                Case(
                    When(order__paid__isnull=False, then=1),
                    output_field=models.IntegerField(),
                )
            )
        )

    def get_or_nothing(self, name: str | None) -> Optional["PromoCode"]:
        if name is not None:
            with contextlib.suppress(PromoCode.DoesNotExist):
                return self.active().get(name__iexact=name.strip())


PromoCodeManager = models.Manager.from_queryset(PromoCodeQuerySet)


class PromoCode(TimestampedModel):
    objects = PromoCodeManager()

    name = models.CharField(_("Promo Code"), max_length=32, unique=True, db_index=True)
    discount_percent = models.IntegerField(_("Discount percent"), null=True, blank=True)
    discount_value = models.IntegerField(_("Discount amount"), null=True, blank=True, help_text=_("Takes precedence over percent"))
    expires = models.DateTimeField(_("Expiration date"), null=True, blank=True)
    active = models.BooleanField(_("Active"), default=True)
    destination = models.TextField(_("Destination"))

    courses = models.ManyToManyField("products.Course", help_text=_("Can not be used for courses not checked here"), blank=True)

    class Meta:
        verbose_name = _("Promo Code")
        verbose_name_plural = _("Promo Codes")
        constraints = [
            CheckConstraint(check=Q(discount_percent__isnull=False) | Q(discount_value__isnull=False), name="percent or value must be set"),
        ]

    def clean(self) -> None:
        if self.discount_percent is None and self.discount_value is None:
            raise ValidationError(_("Percent or value must be set"))

    def compatible_with(self, course: Course) -> bool:
        return self.courses.count() == 0 or course in self.courses.all()

    def apply(self, course: Course) -> Decimal:
        if not self.compatible_with(course):
            return course.price

        if self.discount_value is not None and self.discount_value and self.discount_value < course.price:
            return Decimal(course.price - self.discount_value)

        if self.discount_percent is not None:
            return Decimal(course.price * (100 - self.discount_percent) / 100)

        return course.price
