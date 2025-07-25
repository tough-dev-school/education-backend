from typing import Any

from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class LegacyBundle(TimestampedModel):
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

    # LegacyBundle-specific fields
    records = models.ManyToManyField("products.LegacyRecord")
    courses = models.ManyToManyField("products.Course")

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Bundle")
        verbose_name_plural = _("Bundles")
        db_table = "courses_bundle"

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")
