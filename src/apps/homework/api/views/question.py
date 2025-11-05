from django.db.models import QuerySet
from rest_framework import generics

from apps.homework.api import serializers
from apps.homework.models import Question


class QuestionView(generics.RetrieveAPIView):
    queryset = Question.objects.all()
    serializer_class = serializers.QuestionDetailSerializer
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[Question]:
        queryset = super().get_queryset()

        return queryset.for_user(self.request.user)  # type: ignore
