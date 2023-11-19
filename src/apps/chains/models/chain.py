from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class ChainQuerySet(QuerySet):
    def active(self) -> QuerySet["Chain"]:
        return self.filter(
            sending_is_active=True,
            archived=False,
        )

    def archived(self) -> QuerySet["Chain"]:
        return self.filter(archived=True)

    def editable(self) -> QuerySet["Chain"]:
        return self.filter(
            sending_is_active=False,
            archived=False,
        ).select_related(
            "course",
        )


ChainManager = models.Manager.from_queryset(ChainQuerySet)


class Chain(TimestampedModel):
    objects = ChainManager()

    name = models.CharField(_("Name"), max_length=256)
    course = models.ForeignKey("products.Course", verbose_name=_("Course"), on_delete=models.CASCADE)

    sending_is_active = models.BooleanField(_("Sending is active"), default=False)
    archived = models.BooleanField(_("The chain is archived"), default=False)

    class Meta:
        verbose_name = _("Email chain")
        verbose_name_plural = _("Email chains")
        constraints = [
            models.UniqueConstraint(fields=["name", "course"], name="unique_name_per_course"),
        ]

    def __str__(self) -> str:
        return self.name


__all__ = [
    "Chain",
]
