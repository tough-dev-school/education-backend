from django.db import transaction
from django.db.models import Count
from django.db.models import Q
from django.db.models import QuerySet

from homework.models import Answer
from homework.models import AnswerCrossCheck
from users.models import User


class AnswerCrossCheckDispatcher:
    """Given a bunch of answers and users, create a cross-check record
    for each of them, making sure the first answer of each user has a user to
    check and number of answers if equal for each user
    """

    def __init__(self, answers: QuerySet[Answer], answers_per_user: int = 3):
        self.answers = Answer.objects.filter(pk__in=[answer.pk for answer in answers])
        self.unique_author_answers = self.answers.order_by("author_id", "created").distinct("author_id")
        self.users = User.objects.filter(pk__in=[answer.author_id for answer in answers]).order_by("?")
        self.answers_per_user = answers_per_user

    @transaction.atomic
    def __call__(self) -> list[AnswerCrossCheck]:
        crosschecks = list()
        for user in self.users.iterator():
            for _ in range(self.answers_per_user):
                answer = self.get_answer_to_check(user)
                if answer is not None:
                    crosschecks.append(
                        self.give_answer_to_user(answer, user),
                    )
        return crosschecks

    def get_answer_to_check(self, user: User) -> Answer | None:
        return (
            self.get_answers_with_crosscheck_count()
            .filter(id__in=self.unique_author_answers)
            .annotate(already_checking=Count("answercrosscheck", filter=Q(answercrosscheck__checker_id=user.id)))
            .exclude(already_checking__gte=1)
            .exclude(author=user)
            .exclude(do_not_crosscheck=True)
            .order_by("crosscheck_count")
            .first()
        )

    def give_answer_to_user(self, answer: Answer, user: User) -> AnswerCrossCheck:
        return AnswerCrossCheck.objects.create(answer=answer, checker=user)

    def get_answers_with_crosscheck_count(self) -> QuerySet[Answer]:
        return self.answers.annotate(
            crosscheck_count=Count("answercrosscheck", filter=Q(answercrosscheck__checker__in=self.users)),
        )
