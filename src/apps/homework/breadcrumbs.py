from typing import TYPE_CHECKING

from django.db.models import QuerySet

from apps.homework.models import Question
from apps.lms.models import Lesson
from apps.users.models import User

if TYPE_CHECKING:
    from apps.products.models import Course


def get_lesson(question: Question, user: User) -> Lesson | None:
    """
    Get lesson, attached to course.

    In the future we will remove courses from questions, so this method will only need to find lesson course
    """
    return Lesson.objects.filter(
        question=question,
        module__course__in=_find_courses(question, user),
    ).first()


def _find_courses(question: Question, user: User) -> QuerySet["Course"]:
    queryset = question.courses.all()

    if user.has_perm("studying.purchased_all_courses"):
        return queryset

    return queryset.purchased_by(user)


__all__ = [
    "get_lesson",
]
