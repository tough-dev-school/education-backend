from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type

from django.db.models import QuerySet
from django.utils.functional import cached_property

from apps.homework.models import Answer
from apps.homework.models.answer_cross_check import AnswerCrossCheckQuerySet
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.markdown import markdownify, remove_img
from core.services import BaseService


@dataclass
class BaseAnswerNotification(ABC):
    answer: "Answer"
    user: "User"

    def send_if_should(self) -> bool:
        """
        Send notification if it should be sent and returns True, otherwise returns False
        Please do not override this method, override send instead
        """
        if self.should_send():
            self.send()
            return True

        return False

    @abstractmethod
    def get_template_id(self) -> str:
        """Return template id for notification, should be a string that is used in the mailing service to get the template"""
        ...

    @abstractmethod
    def get_context(self) -> dict:
        """
        Context for template, should be a dictionary with keys and values that will be used in the template
        """
        ...

    @abstractmethod
    def should_send(self) -> bool:
        """
        Return True if notification can be sent, False otherwise
        For example if user is not author of the answer, he should not receive notification
        """
        ...

    def send(self) -> None:
        """Sends notification, rewrite it if you want to use another way of sending"""
        send_mail.delay(
            to=self.user.email,
            template_id=self.get_template_id(),
            ctx=self.get_context(),
            disable_antispam=True,
        )


@dataclass
class DefaultAnswerNotification(BaseAnswerNotification):
    """
    Default notification that is sent to all users that have ever written an answer to the root of the discussion
    """

    def get_template_id(self) -> str:
        return "new-answer-notification"

    def get_context(self) -> dict:
        context = {
            "discussion_name": str(self.answer.question),
            "discussion_url": self.answer.get_absolute_url(),
            "answer_text": self.get_text_with_markdown(),
            "author_name": str(self.answer.author),
        }

        if self.answer.is_author_of_root_answer(self.user):
            context["is_root_answer_author"] = "1"

        context["is_non_root_answer_author"] = "1"

        return context

    def should_send(self) -> bool:
        """This is a default notification, so if no other notification can be sent, this one will be sent"""
        return True

    def get_text_with_markdown(self) -> str:
        return remove_img(markdownify(self.answer.text).strip())


@dataclass
class CrossCheckedAnswerNotification(BaseAnswerNotification):
    """
    Notification about new answer (homework check), which is a part of p2p cross-checking process
    """

    def get_template_id(self) -> str:
        return "crosschecked-answer-notification"

    def get_context(self) -> dict:
        crosschecks = []

        for crosscheck in self.crosschecks.iterator():
            crosschecks.append(
                {
                    "crosscheck_url": crosscheck.answer.get_absolute_url(),
                    "crosscheck_author_name": str(crosscheck.answer.author),
                }
            )

        return {
            "discussion_name": str(self.answer.question),
            "discussion_url": self.answer.get_absolute_url(),
            "author_name": str(self.answer.author),
            "crosschecks": crosschecks,
        }

    def should_send(self) -> bool:
        """
        Notification can be sent if author of homework answer (root answer) has not completed crosscheckes and current answer is a part of crosschecking process
        """
        if not self.answer.is_author_of_root_answer(self.user):
            return False

        if self.answer not in self.answer.get_root_answer().get_first_level_descendants():
            return False

        return self.crosschecks.exists()

    @cached_property
    def crosschecks(self) -> "AnswerCrossCheckQuerySet":
        return self.user.answercrosscheck_set.filter(answer__question=self.answer.question, checked_at__isnull=True)


@dataclass
class NewAnswerNotifier(BaseService):
    """
    Service that determines which user and what kind of notification should be sent
    """

    answer: Answer

    def act(self) -> None:
        for user_to_notify in self.get_users_to_notify().iterator():
            for notification in self.get_notification_classes():
                notification_instance = notification(answer=self.answer, user=user_to_notify)

                if notification_instance.send_if_should():
                    break

    @staticmethod
    def get_notification_classes() -> list[Type[BaseAnswerNotification]]:
        """Be sure to add all new notifications here in correct priority order"""
        return [
            CrossCheckedAnswerNotification,
            DefaultAnswerNotification,
        ]

    def get_users_to_notify(self) -> QuerySet[User]:
        """Get authors of ancestor answers, excluding current answer author"""
        authors = self.answer.ancestors().values_list("author", flat=True)

        authors = list(authors)  # have to execute this query cuz django-tree-queries fails to compile it

        return User.objects.filter(pk__in=authors).exclude(pk=self.answer.author_id)
