from datetime import timedelta
from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from django.conf import settings
from django.utils import timezone

from homework.models import Question


def get_all_purcased_user_ids(question: Question) -> frozenset[int]:
    user_ids: set[int] = set()
    for course in question.courses.all():
        user_ids.update(course.get_purchased_users().values_list("id", flat=True))

    return frozenset(user_ids)


class ShouldHavePurchasedCoursePermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return (
            request.user.has_perm("homework.see_all_questions")
            or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING
            or (request.user.id in get_all_purcased_user_ids(obj))
        )


class ShouldHavePurchasedQuestionCoursePermission(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return (
            request.user.has_perm("homework.see_all_questions")
            or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING
            or (request.user.id in get_all_purcased_user_ids(obj.question))
        )


class ShouldBeAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True

        return False


class MayChangeAnswerOnlyForLimitedTime(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        last_update_time = obj.created if obj.modified is None else obj.modified

        if timezone.now() - last_update_time < timedelta(minutes=30):
            return True

        return False
