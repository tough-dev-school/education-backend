from typing import Optional

import random
from django.db import transaction
from django.db.models import Count, Q, QuerySet

from homework.models import Answer, AnswerCrossCheck
from users.models import User


class AnswerCrossCheckDispatcher:
    """Given a bunch of answers and users, create a cross-check record
    for each of them, making sure each answer has a user to check
    and number of answers if equal for each user
    """
    def __init__(self, answers: list[Answer], answers_per_user: int = 3):
        self.answers = Answer.objects.filter(pk__in=[answer.pk for answer in answers])
        self.users = User.objects.filter(pk__in=[answer.author_id for answer in answers])
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

    def get_answer_to_check(self, user: User) -> Optional[Answer]:
        valid_answers = list(
            self.get_answers_with_crosscheck_count()
            .annotate(already_checking=Count('answercrosscheck', filter=Q(answercrosscheck__checker_id=user.id)))
            .exclude(already_checking__gte=1)
            .exclude(author=user)
            .exclude(do_not_crosscheck=True)
            .order_by('crosscheck_count'))

        if len(valid_answers) >= 1:
            return random.choices(valid_answers, weights=[len(valid_answers) - answer.crosscheck_count for answer in valid_answers])[0]

        return None

    def give_answer_to_user(self, answer: Answer, user: User) -> AnswerCrossCheck:
        return AnswerCrossCheck.objects.create(answer=answer, checker=user)

    def get_answers_with_crosscheck_count(self) -> QuerySet[Answer]:
        return self.answers.annotate(
            crosscheck_count=Count('answercrosscheck', filter=Q(answercrosscheck__checker__in=self.users)),
        )
