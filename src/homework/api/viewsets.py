from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.viewsets import AppViewSet
from homework.api.filtersets import AnswerFilterSet
from homework.api.permissions import (
    MayChangeAnswerOnlyForLimitedTime, ShouldBeAnswerAuthorOrReadOnly, ShouldHavePurchasedQuestionCoursePermission)
from homework.api.serializers import AnswerCreateSerializer, AnswerTreeSerializer
from homework.models import Answer, AnswerAccessLogEntry
from homework.models.answer import AnswerQuerySet


class AnswerViewSet(AppViewSet):
    queryset = Answer.objects.for_viewset()
    serializer_class = AnswerTreeSerializer
    serializer_action_classes = {
        'create': AnswerCreateSerializer,
        'partial_update': AnswerCreateSerializer,
    }

    lookup_field = 'slug'
    permission_classes = [
        IsAuthenticated &
        ShouldHavePurchasedQuestionCoursePermission &
        ShouldBeAnswerAuthorOrReadOnly &
        MayChangeAnswerOnlyForLimitedTime,
    ]
    filterset_class = AnswerFilterSet

    def update(self, request: Request, *args, **kwargs) -> Response:
        if not kwargs.get('partial', False):
            raise MethodNotAllowed('Please use patch')

        response = super().update(request, *args, **kwargs)  # type: ignore

        answer = self.get_object()
        answer.refresh_from_db()
        Serializer = self.get_serializer_class(action='retrieve')
        response.data = Serializer(answer).data

        return response

    def get_queryset(self) -> AnswerQuerySet:
        queryset = super().get_queryset()

        queryset = self.limit_queryset_to_user(queryset)  # type: ignore

        return self.limit_queryset_for_list(queryset)

    def limit_queryset_to_user(self, queryset: AnswerQuerySet) -> AnswerQuerySet:
        if not self.request.user.has_perm('homework.see_all_answers') and self.action != 'retrieve':
            return queryset.for_user(self.request.user)  # type: ignore

        return queryset

    def limit_queryset_for_list(self, queryset: AnswerQuerySet) -> AnswerQuerySet:
        if self.action == 'list':
            return queryset.root_only()

        return queryset

    def get_object(self) -> Answer:
        """Write a log entry for each answer from another user that is retrieved
        """
        instance = super().get_object()

        self.write_log_entry(answer=instance)

        return instance

    def write_log_entry(self, answer: Answer) -> None:
        if not self.request.user.has_perm('homework.see_all_answers'):
            if answer.author != self.request.user:
                AnswerAccessLogEntry.objects.get_or_create(
                    user=self.request.user,
                    answer=answer,
                )
