from typing import Any, Protocol, Sequence

from rest_framework.request import Request

from django.db.models import QuerySet


class BaseListAPIView(Protocol):
    @property
    def pagination_disabled(self) -> bool:
        ...

    @property
    def request(self) -> Request:
        ...

    def paginate_queryset(self, queryset: QuerySet | Sequence[Any]) -> None | Sequence[Any]:
        ...


class DisablePaginationWithQueryParamMixin:
    """Add ability to disable response pagination with `disable_pagination=True` query param."""

    @property
    def pagination_disabled(self: BaseListAPIView) -> bool:
        return str(self.request.query_params.get("disable_pagination", False)).lower() in [
            "true",
            "1",
        ]

    def paginate_queryset(self: BaseListAPIView, queryset: QuerySet | Sequence[Any]) -> None | Sequence[Any]:
        if self.pagination_disabled:
            return None

        return super().paginate_queryset(queryset)
