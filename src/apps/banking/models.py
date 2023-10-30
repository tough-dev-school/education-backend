from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from core.models import models
from core.models import TimestampedModel


class Receipt(TimestampedModel):
    class PROVIDERS(TextChoices):
        ATOL = "atol", _("Atol")

    provider = models.CharField(max_length=16, db_index=True, choices=PROVIDERS.choices)
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT)
    source_ip = models.GenericIPAddressField()

    data = models.JSONField(default=dict)

    class Meta:
        verbose_name = _("Receipt")
        verbose_name_plural = _("Receipts")
