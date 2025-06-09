from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.lms.api.filters import ModuleFilterSet
from apps.lms.api.serializers import ModuleSerializer
from apps.lms.models import Module
from apps.lms.models.module import ModuleQuerySet
from core.api.mixins import DisablePaginationWithQueryParamMixin


class ModuleListView(DisablePaginationWithQueryParamMixin, ListAPIView):
    """List modules, accessible to user. Better use it filtering by course"""

    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ModuleFilterSet
    queryset = Module.objects.for_viewset()

    def get_queryset(self) -> ModuleQuerySet:
        queryset: ModuleQuerySet = super().get_queryset()  # type: ignore

        if self.request.user.has_perm("studying.purchased_all_courses"):
            return queryset

        return queryset.for_user(self.request.user)  # type: ignore
