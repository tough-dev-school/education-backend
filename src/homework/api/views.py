from rest_framework import serializers
from rest_framework.generics import RetrieveAPIView

from homework.api.serializers import QuestionSerializer
from homework.models import Question


class QuestionView(RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    lookup_field = 'slug'
