from typing import Any

from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class LegacyRecord(TimestampedModel):
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

    course = models.ForeignKey("products.Course", on_delete=models.CASCADE)
    s3_object_id = models.CharField(max_length=512)
    template_id = models.CharField(_("Postmark template_id"), max_length=256, blank=True, null=True, help_text=_("Leave it blank for the default template"))

    class Meta:
        ordering = ["-id"]
        verbose_name = _("Record")
        verbose_name_plural = _("Records")
        db_table = "courses_record"

    def save(self, *args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Deprecated model")
