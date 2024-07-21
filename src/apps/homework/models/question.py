import uuid
from typing import Any
from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Question(TimestampedModel):
    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    courses = models.ManyToManyField("products.Course")
    name = models.CharField(_("Name"), max_length=256)
    hide_crosschecked_answers_from_students_without_checks = models.BooleanField(_("Hide crosschecked answers from students without checks"), default=False)

    text = models.TextField()

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

        self.hide_crosschecked_answers_from_students_without_checks = True  # there are active courses now, so we shan't touch them
        self.save()

        return dispatcher()
