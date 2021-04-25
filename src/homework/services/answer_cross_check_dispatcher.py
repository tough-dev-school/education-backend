from typing import List, Optional

from django.db import transaction
from django.db.models import Count, Q

from homework.models import Answer, AnswerCrossCheck
from users.models import User


class AnswerCrossCheckDispatcher:
    """Given a bunch of answers and users, create a cross-check record for each of them, making sure each answer has a user to check it and number of answers to check if equal for each user
    """
    def __init__(self, answers: List[Answer]):
        self.answers = Answer.objects.filter(pk__in=[answer.pk for answer in answers])
        self.users = User.objects.filter(pk__in=[answer.author_id for answer in answers])

    @transaction.atomic
    def __call__(self) -> List[AnswerCrossCheck]:
        cross_checks = list()
        for answer in self.answers.iterator():
            user = self.get_user_to_check(answer)
            cross_checks.append(
                self.give_answer_to_user(answer, user),
            )

        return cross_checks

    def get_user_to_check(self, answer: Answer) -> Optional[User]:
        return self.get_users_with_cross_check_count() \
            .annotate(already_checking=Count('answercrosscheck', filter=Q(answercrosscheck__answer_id=answer.id))) \
            .exclude(already_checking__gte=1) \
            .exclude(id=answer.author_id) \
            .order_by('crosscheck_count') \
            .first()

    def give_answer_to_user(self, answer: Answer, user: User):
        return AnswerCrossCheck.objects.create(answer=answer, checker=user)

    def get_users_with_cross_check_count(self):
        return self.users.annotate(
            crosscheck_count=Count('answercrosscheck', filter=Q(answercrosscheck__answer__in=self.answers)),
        )
