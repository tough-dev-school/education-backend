from typing import FrozenSet

from django.conf import settings
from rest_framework import permissions

from homework.models import Question


def get_all_purcased_user_ids(question: Question) -> FrozenSet[int]:
    user_ids = set()
    for course in question.courses.all():
        user_ids.update(course.get_purchased_users().values_list('id', flat=True))

    return frozenset(user_ids)


class ShouldHavePurchasedCoursePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('homework.see_all_questions') or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or (request.user.id in get_all_purcased_user_ids(obj))


class ShouldHavePurchasedQuestionCoursePermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('homework.see_all_questions') or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or (request.user.id in get_all_purcased_user_ids(obj.question))
