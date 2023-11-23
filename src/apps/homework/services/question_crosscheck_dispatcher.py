from dataclasses import dataclass

from django.db.models import QuerySet

from apps.homework.models import Answer
from apps.homework.models import AnswerCrossCheck
from apps.homework.models import Question
from apps.homework.services.answer_crosscheck_dispatcher import AnswerCrossCheckDispatcher
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.services import BaseService


@dataclass
class QuestionCrossCheckDispatcher(BaseService):
    question: Question
    answers_per_user: int = 3

    def __post_init__(self) -> None:
        self.dispatcher = AnswerCrossCheckDispatcher(
            answers=self.get_answers_to_check(),
            answers_per_user=self.answers_per_user,
        )

        self.checks: list[AnswerCrossCheck] = list()

    def act(self) -> int:
        self.dispatch_crosschecks()
        self.notify_users()

        return self.get_users_to_notify().count()

    def dispatch_crosschecks(self) -> None:
        self.checks = self.dispatcher()

    def notify_users(self) -> None:
        for user in self.get_users_to_notify():
            user_checks_list = self.get_checks_for_user(user)
            send_mail.delay(
                to=user.email,
                template_id="new-answers-to-check",
                ctx=self.get_notification_context(user_checks_list),
                disable_antispam=True,
            )

    def get_users_to_notify(self) -> QuerySet[User]:
        return User.objects.filter(pk__in=[check.checker_id for check in self.checks])

    def get_checks_for_user(self, user: User) -> list[AnswerCrossCheck]:
        return [check for check in self.checks if check.checker == user]

    def get_answers_to_check(self) -> QuerySet[Answer]:
        return (
            Answer.objects.filter(question=self.question)
            .root_only()
            .exclude(
                do_not_crosscheck=True,
            )
        )

    @staticmethod
    def get_notification_context(checks: list[AnswerCrossCheck]) -> dict:
        answers = list()

        for check in checks:
            answers.append(
                {
                    "url": check.answer.get_absolute_url(),
                    "text": str(check.answer),
                }
            )

        return {
            "answers": answers,
        }
