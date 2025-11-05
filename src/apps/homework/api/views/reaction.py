from typing import Any

from django.db.models import QuerySet
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.homework.api.permissions import AuthorOrReadonly
from apps.homework.api.serializers import (
    ReactionCreateSerializer,
    ReactionDetailedSerializer,
)
from apps.homework.models import Answer
from apps.homework.models.reaction import Reaction
from apps.homework.services import ReactionCreator
from core.viewsets import CreateDeleteAppViewSet


class ReactionViewSet(CreateDeleteAppViewSet):
    queryset = Reaction.objects.for_viewset()
    serializer_class = ReactionDetailedSerializer
    serializer_action_classes = {
        "create": ReactionCreateSerializer,
    }
    permission_classes = [IsAuthenticated & AuthorOrReadonly]

    lookup_field = "slug"

    @extend_schema(request=ReactionCreateSerializer, responses=ReactionDetailedSerializer)
    def create(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        """Create a reaction"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data.copy()
        reaction = ReactionCreator(emoji=data.get("emoji"), slug=data.get("slug"), author=self.request.user, answer=self.answer)()  # type: ignore

        Serializer = self.get_serializer_class(action="retrieve")
        return Response(Serializer(reaction).data, status=201)

    def get_queryset(self) -> QuerySet[Reaction]:
        return super().get_queryset().filter(answer=self.answer)

    @cached_property
    def answer(self) -> Answer:
        return get_object_or_404(Answer, slug=self.kwargs.get("answer_slug"))
