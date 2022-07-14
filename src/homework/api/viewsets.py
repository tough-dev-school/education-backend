from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated

from app.viewsets import AppViewSet
from homework.api.filtersets import AnswerFilterSet
from homework.api.permissions import (
    MayDeleteAnswerOnlyForLimitedTime, ShouldBeAnswerAuthorOrReadOnly, ShouldHavePurchasedQuestionCoursePermission)
from homework.api.serializers import AnswerCreateSerializer, AnswerTreeSerializer
from homework.models import Answer, AnswerAccessLogEntry


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
        MayDeleteAnswerOnlyForLimitedTime,
    ]
    filterset_class = AnswerFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()

        queryset = self.limit_queryset_to_user(queryset)

        return self.limit_queryset_for_list(queryset)

    def limit_queryset_to_user(self, queryset):
        if not self.request.user.has_perm('homework.see_all_answers') and self.action != 'retrieve':
            return queryset.for_user(self.request.user)

        return queryset

    def limit_queryset_for_list(self, queryset):
        if self.action == 'list':
            return queryset.root_only()

        return queryset

    def get_object(self):
        """Write a log entry for each answer from another user that is retrieved
        """
        instance = super().get_object()

        self.write_log_entry(answer=instance)

        return instance

    def write_log_entry(self, answer):
        if not self.request.user.has_perm('homework.see_all_answers'):
            if answer.author != self.request.user:
                AnswerAccessLogEntry.objects.get_or_create(
                    user=self.request.user,
                    answer=answer,
                )
