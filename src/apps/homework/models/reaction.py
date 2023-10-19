import uuid

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from app.models import models
from app.models import TimestampedModel


class ReactionQuerySet(QuerySet):
    def for_viewset(self) -> "ReactionQuerySet":
        return self.select_related("author", "answer")


class Reaction(TimestampedModel):
    MAX_REACTIONS_FROM_ONE_AUTHOR = 3

    objects = models.Manager.from_queryset(ReactionQuerySet)()

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)

    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="reactions")
    answer = models.ForeignKey("homework.Answer", on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=10)

    class Meta:
        verbose_name = _("Reaction")
        verbose_name_plural = _("Reactions")
        ordering = ["created"]
        constraints = [
            models.UniqueConstraint(
                fields=["author", "answer", "emoji"],
                name="Unique emoji per author",
            ),
        ]
