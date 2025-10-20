from typing import Any

from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.homework.api.filtersets import AnswerFilterSet
from apps.homework.api.permissions import (
    AuthorOrReadonly,
    IsEditable,
)
from apps.homework.api.serializers import (
    AnswerCreateSerializer,
    AnswerSerializer,
    AnswerTreeSerializer,
    AnswerUpdateSerializer,
    ReactionCreateSerializer,
    ReactionDetailedSerializer,
)
from apps.homework.models import Answer
from apps.homework.models.answer import AnswerQuerySet
from apps.homework.models.reaction import Reaction
from apps.homework.services import AnswerCreator, AnswerRemover, AnswerUpdater, ReactionCreator
from apps.users.models import User
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.viewsets import AppViewSet, CreateDeleteAppViewSet


@method_decorator(
    extend_schema(
        description="List allowed answers",
    ),
    name="list",
)
@method_decorator(
    extend_schema(
        description="Get an answer by slug (any answer can be accessible if user knows the slug",
        responses=AnswerTreeSerializer,
    ),
    name="retrieve",
)
class AnswerViewSet(DisablePaginationWithQueryParamMixin, AppViewSet):
    """Answer CRUD"""

    queryset = Answer.objects.for_viewset()
    serializer_class = AnswerSerializer
    serializer_action_classes = {
        "partial_update": AnswerUpdateSerializer,
        "retrieve": AnswerTreeSerializer,
    }

    lookup_field = "slug"
    permission_classes = [
        IsAuthenticated & AuthorOrReadonly & IsEditable,
    ]
    filterset_class = AnswerFilterSet

    @extend_schema(request=AnswerCreateSerializer, responses=AnswerTreeSerializer)
    def create(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        """Create an answer"""

        answer = AnswerCreator(
            question_slug=request.data.get("question"),
            parent_slug=request.data.get("parent"),
            content=request.data.get("content", {}),
        )()

        answer = self.get_queryset().get(pk=answer.pk)  # augment answer with annotations from .for_viewset() to display it properly
        Serializer = self.get_serializer_class(action="retrieve")
        return Response(
            Serializer(
                answer,
                context=self.get_serializer_context(),
            ).data,
            status=201,
        )

    @extend_schema(request=AnswerUpdateSerializer, responses=AnswerTreeSerializer)
    def update(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        """Update answer text"""

        if not kwargs.get("partial", False):
            raise MethodNotAllowed("Please use patch")

        AnswerUpdateSerializer(data=request.data).is_valid(raise_exception=True)

        answer = self.get_object()
        answer = AnswerUpdater(
            answer=self.get_object(),
            content=request.data["content"],
        )()

        Serializer = self.get_serializer_class(action="retrieve")
        return Response(
            Serializer(
                answer,
                context=self.get_serializer_context(),
            ).data,
            status=200,
        )

    def destroy(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        """Remove an answer if allowed"""
        AnswerRemover(instance=self.get_object())()
        return Response(status=204)

    def get_queryset(self) -> AnswerQuerySet:
        queryset = super().get_queryset()

        queryset = self.limit_queryset_to_user(queryset)
        queryset = self.limit_queryset_for_list(queryset)

        return queryset.with_children_count().order_by("created").prefetch_reactions()

    def limit_queryset_to_user(self, queryset: AnswerQuerySet) -> AnswerQuerySet:
        if self.action != "retrieve" and not self.user.has_perm("homework.see_all_answers"):
            # Each user may access any answer knowing its slug
            return queryset.for_user(self.user)

        return queryset

    def limit_queryset_for_list(self, queryset: AnswerQuerySet) -> AnswerQuerySet:
        if self.action == "list":
            return queryset.root_only()

        return queryset

    @property
    def user(self) -> User:
        return self.request.user


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
        reaction = ReactionCreator(emoji=data.get("emoji"), slug=data.get("slug"), author=self.request.user, answer=self.answer)()

        Serializer = self.get_serializer_class(action="retrieve")
        return Response(Serializer(reaction).data, status=201)

    def get_queryset(self) -> QuerySet[Reaction]:
        return super().get_queryset().filter(answer=self.answer)

    @cached_property
    def answer(self) -> Answer:
        return get_object_or_404(Answer, slug=self.kwargs.get("answer_slug"))
