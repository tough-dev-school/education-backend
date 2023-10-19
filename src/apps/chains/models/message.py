from datetime import timedelta

from django.apps import apps
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.studying.models import Study
from core.models import models
from core.models import TimestampedModel


class MessageQuerySet(QuerySet):
    def may_be_parent(self) -> QuerySet["Message"]:
        return self.filter(
            chain__sending_is_active=False,
            children__isnull=True,
        ).select_related(
            "chain",
            "chain__course",
        )

    def not_archived(self) -> QuerySet["Message"]:
        return self.filter(chain__archived=False)


MessageManager = models.Manager.from_queryset(MessageQuerySet)


class Message(TimestampedModel):
    objects = MessageManager()

    name = models.CharField(_("Name"), max_length=256)
    chain = models.ForeignKey("chains.Chain", verbose_name=_("Chain"), on_delete=models.CASCADE)
    template_id = models.CharField(_("Template id"), max_length=256)

    parent = models.ForeignKey(
        "chains.Message",
        on_delete=models.PROTECT,
        verbose_name=_("Parent"),
        related_name="children",
        null=True,
        blank=True,
        help_text=_("Messages without parent will be sent upon start"),
    )

    delay = models.BigIntegerField(_("Delay (minutes)"), default=0, help_text=_("1440 for day, 10080 for week"))

    class Meta:
        verbose_name = _("Email chain message")
        verbose_name_plural = _("Email chain messages")
        constraints = [
            models.UniqueConstraint(fields=["name", "chain"], name="unique_name_per_chain"),
        ]

    def __str__(self) -> str:
        return f"{self.chain.course}, {self.chain} {self.name}"

    def time_to_send(self, study: Study) -> bool:
        if self.parent is None:
            return False

        previous_message_progress = apps.get_model("chains.Progress").objects.filter(study=study, message=self.parent).first()

        if previous_message_progress is None:
            return False

        return timezone.now() - previous_message_progress.created > timedelta(minutes=self.delay)


__all__ = [
    "Message",
]
