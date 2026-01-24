from typing import Any

from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.homework.api import serializers
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
)
from apps.homework.models import Answer, AnswerAttachment, AnswerImage
from apps.homework.models.answer import AnswerQuerySet
from apps.homework.services import AnswerCreator, AnswerRemover, AnswerUpdater
from apps.users.models import User
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.api.swagger.fields import BinaryUploadField
from core.viewsets import AppViewSet


@method_decorator(
    extend_schema(
        request=inline_serializer(
            name="AnswerImageRequestSerializer",
            fields={
                "image": BinaryUploadField(),
            },
        ),
        examples=[
            OpenApiExample(
                name="Default response",
                response_only=True,
                status_codes=[201],
                value={
                    "image": "https://cdn.tough-dev.school/homework/answers/typicalmacuser.jpg",
                },
            ),
        ],
    ),
    name="post",
)
class ImageUploadView(generics.CreateAPIView):
    """Upload an image"""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AnswerImageSerializer
    queryset = AnswerImage.objects.all()
    parser_classes = [MultiPartParser]


@method_decorator(
    extend_schema(
        request=inline_serializer(
            name="AnswerAttachmentRequestSerializer",
            fields={
                "file": BinaryUploadField(),
            },
        ),
        examples=[
            OpenApiExample(
                name="Default response",
                response_only=True,
                status_codes=[201],
                value={
                    "file": "https://cdn.tough-dev.school/homework/attachments/document.pdf",
                },
            ),
        ],
    ),
    name="post",
)
class AttachmentUploadView(generics.CreateAPIView):
    """Upload an attachment (PDF only)"""

    permission_classes = [IsAuthenticated]
    serializer_class = serializers.AnswerAttachmentSerializer
    queryset = AnswerAttachment.objects.all()
    parser_classes = [MultiPartParser]


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
            question_slug=request.data.get("question"),  # type: ignore
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

        queryset = self.limit_queryset_to_user(queryset)  # type: ignore
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
        return self.request.user  # type: ignore
