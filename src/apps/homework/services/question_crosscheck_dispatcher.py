from dataclasses import dataclass

from django.db.models import QuerySet

from apps.homework.models import Answer, AnswerCrossCheck, Question
from apps.homework.services.answer_crosscheck_dispatcher import AnswerCrossCheckDispatcher
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.services import BaseService


@dataclass
class QuestionCrossCheckDispatcher(BaseService):
    question: Question
    answers_per_user: int = 3

    def act(self) -> int:
        self.crosschecks = self.dispatch_crosschecks()
        self.notify_users()

        return self.get_users_to_notify().count()

    def dispatch_crosschecks(self) -> list[AnswerCrossCheck]:
        dispatcher = AnswerCrossCheckDispatcher(
            answers=self.get_answers_to_check(),
            answers_per_user=self.answers_per_user,
        )
        return dispatcher()

    def notify_users(self) -> None:
        for user in self.get_users_to_notify():
            user_crosschecks_list = self.get_crosschecks_for_user(user)
            send_mail.delay(
                to=user.email,
                template_id="new-answers-to-check",
                ctx=self.get_notification_context(user_crosschecks_list),
                disable_antispam=True,
            )

    def get_users_to_notify(self) -> QuerySet[User]:
        return User.objects.filter(pk__in=[check.checker_id for check in self.crosschecks])

    def get_crosschecks_for_user(self, user: User) -> list[AnswerCrossCheck]:
        return [crosscheck for crosscheck in self.crosschecks if crosscheck.checker == user]

    def get_answers_to_check(self) -> QuerySet[Answer]:
        return (
            Answer.objects.filter(question=self.question)
            .root_only()
            .exclude(
                do_not_crosscheck=True,
            )
        )

    @staticmethod
    def get_notification_context(crosschecks: list[AnswerCrossCheck]) -> dict:
        answers = list()

        for crosscheck in crosschecks:
            answers.append(
                {
                    "url": crosscheck.answer.get_absolute_url(),
                    "text": str(crosscheck.answer),
                }
            )

        return {
            "answers": answers,
        }
