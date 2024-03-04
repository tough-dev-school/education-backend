from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.homework.models import Question


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

        if timezone.now() - obj.created < timedelta(days=1):
            return True

        return False


class MayChangeAnswerOnlyWithoutDescendants(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.get_first_level_descendants().count() == 0:
            return True

        return False
