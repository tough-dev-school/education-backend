from typing import FrozenSet

from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import permissions

from homework.models import Question


def get_all_purcased_user_ids(question: Question) -> FrozenSet[int]:
    user_ids = set()
    for course in question.courses.all():
        user_ids.update(course.get_purchased_users().values_list('id', flat=True))

    return frozenset(user_ids)


class ShouldHavePurchasedCoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('homework.see_all_questions') or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or (request.user.id in get_all_purcased_user_ids(obj))


class ShouldHavePurchasedQuestionCoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING:
            return True

        if request.method == 'POST':
            question = self.get_question(view.kwargs['question_slug'])

            return request.user.id in get_all_purcased_user_ids(question)

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('homework.see_all_questions') or settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING or (request.user.id in get_all_purcased_user_ids(obj.question))

    def get_question(self, slug):
        return get_object_or_404(Question, slug=slug)
