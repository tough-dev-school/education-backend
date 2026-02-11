from dataclasses import dataclass

from django.db.models import QuerySet

from apps.homework.models import Answer, AnswerCrossCheck, Question
from apps.homework.services.answer_crosscheck_dispatcher import AnswerCrossCheckDispatcher
from apps.lms.models import Lesson
from apps.mailing.tasks import send_mail
from apps.users.models import User
from core.services import BaseService


@dataclass
class QuestionCrossCheckDispatcher(BaseService):
    """Dispatches crosschecks for given question (and its neighbours).

    To improve readability, the user story is split in 2 services:
        - QuestionCrossCheckDispatcher (this one) finds the answers to mix between students
        - AnswerCrossCheckDispatcher mixes them between students
    """

    question: Question
    author: User
    answers_per_user: int = 3

    def act(self) -> int:
        self.crosschecks = self.dispatch_crosschecks()
        self.notify_users()

        return self.get_users_to_notify().count()

    def dispatch_crosschecks(self) -> list[AnswerCrossCheck]:
        dispatcher = AnswerCrossCheckDispatcher(
            answers=self.get_answers_to_check(),
            author=self.author,
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
        questions = self.get_questions_to_check()
        return (
            Answer.objects.filter(question__in=questions)
            .root_only()
            .exclude(
                do_not_crosscheck=True,
            )
        )

    def get_questions_to_check(self) -> QuerySet[Question]:
        """
        Questions with the same name that belong to the same product.group
        """
        current_lesson = Lesson.objects.filter(question=self.question).first()
        if current_lesson is None:
            return Question.objects.filter(pk=self.question.pk)

        same_group_lessons = Lesson.objects.filter(
            module__course__group=current_lesson.module.course.group,
            question__name__iexact=self.question.name,
        )

        return Question.objects.filter(
            pk__in=same_group_lessons.values_list("question_id"),
        )

    @staticmethod
    def get_notification_context(crosschecks: list[AnswerCrossCheck]) -> dict:
        answers = list()

        for crosscheck in crosschecks:
            answers.append(
                {
                    "url": crosscheck.answer.get_absolute_url(),
                    "text": str(crosscheck.answer) if len(str(crosscheck.answer)) > 0 else crosscheck.answer.get_absolute_url(),
                }
            )

        return {
            "answers": answers,
        }
