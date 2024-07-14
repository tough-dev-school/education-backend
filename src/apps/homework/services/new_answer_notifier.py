from dataclasses import dataclass

from django.db.models import QuerySet
from django.utils.functional import cached_property

from apps.homework.models import Answer
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.markdown import markdownify, remove_img
from core.services import BaseService


@dataclass
class NewAnswerNotifier(BaseService):
    answer: Answer

    def act(self) -> None:
        for user_to_notify in self.get_users_to_notify().iterator():
            self.send_mail_to_user(user_to_notify)

    @cached_property
    def root_answer(self) -> Answer:
        return self.answer.get_root_answer()

    def send_mail_to_user(self, user: User) -> None:
        send_mail.delay(
            to=user.email,
            template_id="new-answer-notification",
            ctx=self.get_notification_context(user),
            disable_antispam=True,
        )

    def get_users_to_notify(self) -> QuerySet[User]:
        """Get all users that have ever written an answer to the root of the disqussion"""
        authors = self.answer.get_root_answer().descendants(include_self=True).values_list("author", flat=True)

        authors = list(authors)  # have to execute this query cuz django-tree-queries fails to compile it

        return User.objects.filter(pk__in=authors).exclude(pk=self.answer.author_id)

    def get_notification_context(self, user: User) -> dict:
        context = {
            "discussion_name": str(self.answer.question),
            "discussion_url": self.answer.get_absolute_url(),
            "answer_text": self.get_text_with_markdown(),
            "author_name": str(self.answer.author),
        }

        context.update(self.get_root_answer_context(user))
        context.update(self.get_crosschecks_context(user))

        return context

    def get_root_answer_context(self, user: User) -> dict:
        if user == self.root_answer.author:
            return {"is_root_answer_author": "1"}

        return {"is_non_root_answer_author": "1"}

    def get_crosschecks_context(self, user: User) -> dict:
        crosschecks = user.answercrosscheck_set.filter(answer__question=self.answer.question, checked_at__isnull=True)

        user_is_not_root_answer_author = user != self.root_answer.author
        answer_parent_is_not_root_answer = self.answer.parent != self.root_answer

        if user_is_not_root_answer_author or answer_parent_is_not_root_answer or not crosschecks.exists():
            return {"without_not_checked_crosschecks": "1"}

        context: dict[str, list] = {
            "crosschecks": [],
        }

        for crosscheck in crosschecks.iterator():
            context["crosschecks"].append(
                {
                    "crosscheck_url": crosscheck.answer.get_absolute_url(),
                    "crosscheck_author_name": str(crosscheck.answer.author),
                }
            )

        return context

    def get_text_with_markdown(self) -> str:
        return remove_img(markdownify(self.answer.text).strip())
