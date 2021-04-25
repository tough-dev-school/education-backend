from typing import Iterable, List

from app.tasks import send_mail
from homework.models import AnswerCrossCheck, Question
from homework.services.answer_cross_check_dispatcher import AnswerCrossCheckDispatcher
from users.models import User


class QuestionCrossCheckDispatcher:
    def __init__(self, question: Question, answers_per_user: int = 3):
        self.question = question
        self.dispatcher = AnswerCrossCheckDispatcher(answers=self.question.answer_set.all(), answers_per_user=answers_per_user)
        self.checks: List[AnswerCrossCheck] = list()

    def __call__(self):
        self.dispatch_cross_checks()
        self.notify_users()

    def dispatch_cross_checks(self):
        self.checks = self.dispatcher()

    def notify_users(self):
        for user in self.get_users_to_notify():
            user_checks_list = self.get_checks_for_user(user)
            send_mail.delay(
                to=user.email,
                template_id='new-answers-to-check',
                ctx=self.build_notification_context(user_checks_list),
            )

    def get_users_to_notify(self) -> Iterable[User]:
        return User.objects.filter(pk__in=[check.checker_id for check in self.checks])

    def get_checks_for_user(self, user: User) -> List[AnswerCrossCheck]:
        return [check for check in self.checks if check.checker == user]

    @staticmethod
    def build_notification_context(checks: List[AnswerCrossCheck]):
        answers = list()

        for check in checks:
            answers.append({
                'url': check.answer.get_absolute_url(),
                'text': str(check.answer),
            })

        return {
            'answers': answers,
        }
