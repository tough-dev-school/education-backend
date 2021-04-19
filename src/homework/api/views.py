from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView

from homework.api.permissions import ShouldHavePurchasedCoursePermission, ShouldHavePurchasedQuestionCoursePermission
from homework.api.serializers import AnswerCreateSerializer, AnswerSerializer, QuestionSerializer
from homework.models import Answer, AnswerAccessLogEntry, Question


class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [ShouldHavePurchasedCoursePermission]
    lookup_field = 'slug'


class AnswerView(RetrieveAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    lookup_field = 'slug'
    permission_classes = [ShouldHavePurchasedQuestionCoursePermission]

    def get_question(self):
        return get_object_or_404(Question, slug=self.kwargs['question_slug'])

    def get_queryset(self):
        question = self.get_question()

        return super().get_queryset().filter(question=question)

    def get_object(self):
        """Write a log entry for each answer from another user that is retrieved
        """
        instance = super().get_object()

        self.write_log_entry(answer=instance)

        return instance

    def write_log_entry(self, answer):
        if not self.request.user.has_perm('homework.see_all_answers'):
            if answer.author != self.request.user:
                AnswerAccessLogEntry.objects.create(
                    user=self.request.user,
                    answer=answer,
                )

class AnswerCreateView(ListCreateAPIView):
    queryset = Answer.objects.all()
    permission_classes = [ShouldHavePurchasedQuestionCoursePermission]
    serializer_class = AnswerSerializer

    def get_question(self):
        return get_object_or_404(Question, slug=self.kwargs['question_slug'])

    def create(self, request, *args, **kwargs):
        request.POST._mutable = True
        request.data['question'] = self.get_question().pk

        return super().create(request, *args, **kwargs)

    def get_serializer_class(self):
        """Special serializer for submitting answers"""
        if self.request.method == 'POST':
            return AnswerCreateSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        if not self.request.user.has_perm('homework.see_all_answers'):
            return super().get_queryset().for_author(self.request.user)

        return super().get_queryset()
