from app.viewsets import AppViewSet
from homework.api.filtersets import AnswerFilterSet
from homework.api.permissions import ShouldBeAnswerAuthorOrReadOnly, ShouldHavePurchasedQuestionCoursePermission
from homework.api.serializers import AnswerCreateSerializer, AnswerTreeSerializer
from homework.models import Answer, AnswerAccessLogEntry


class AnswerViewSet(AppViewSet):
    queryset = Answer.objects.with_tree_fields()
    serializer_class = AnswerTreeSerializer
    serializer_action_classes = {
        'create': AnswerCreateSerializer,
    }
    lookup_field = 'slug'
    permission_classes = [ShouldHavePurchasedQuestionCoursePermission & ShouldBeAnswerAuthorOrReadOnly]
    filterset_class = AnswerFilterSet

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.has_perm('homework.see_all_answers') and self.action != 'retrieve':
            return queryset.for_user(self.request.user)

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
