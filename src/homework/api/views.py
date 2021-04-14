from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView

from homework.api.permissions import ShouldHavePurchasedCoursePermission, ShouldHavePurchasedQuestionCoursePermission
from homework.api.serializers import AnswerSerializer, QuestionSerializer
from homework.models import Answer, Question


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
