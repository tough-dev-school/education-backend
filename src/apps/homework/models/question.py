import uuid
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class QuestionQuerySet(QuerySet):
    def for_admin(self) -> "QuestionQuerySet":
        return self.prefetch_related("courses", "courses__group")


class Question(TimestampedModel):
    objects = QuestionQuerySet.as_manager()

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    courses = models.ManyToManyField("products.Course")
    name = models.CharField(_("Name"), max_length=256)

    text = models.TextField()

    deadline = models.DateTimeField(_("Deadline"), null=True, blank=True)

    class Meta:
        verbose_name = _("Homework")
        verbose_name_plural = _("Homeworks")
        permissions = [
            ("see_all_questions", _("May see questions for all homeworks")),
        ]

    def get_absolute_url(self) -> str:
        return urljoin(settings.FRONTEND_URL, f"homework/question-admin/{self.slug}/")

    def dispatch_crosscheck(self, **kwargs: dict[str, Any]) -> int:
        from apps.homework.services import QuestionCrossCheckDispatcher

        dispatcher = QuestionCrossCheckDispatcher(question=self, **kwargs)  # type: ignore

        return dispatcher()
