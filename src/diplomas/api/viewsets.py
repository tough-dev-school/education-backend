
from rest_framework.exceptions import MethodNotAllowed

from app.viewsets import AppViewSet
from diplomas.api.permissions import DiplomaPermission
from diplomas.api.serializers import DiplomaCreateSerializer, DiplomaSerializer
from diplomas.models import Diploma


class DiplomaViewSet(AppViewSet):
    queryset = Diploma.objects.for_viewset()
    lookup_field = 'slug'
    serializer_class = DiplomaSerializer
    serializer_action_classes = {
        'create': DiplomaCreateSerializer,
    }
    permission_classes = [DiplomaPermission]

    def get_queryset(self):
        """Filter diplomas only for current user"""
        queryset = super().get_queryset()

        if self.action != 'retrieve' and not self.request.user.has_perm('diplomas.access_all_diplomas'):
            queryset = queryset.for_user(self.request.user)

        return queryset

    def update(self, request, **kwargs):
        raise MethodNotAllowed(request.method)

    def destroy(self, request, **kwargs):
        raise MethodNotAllowed(request.method)
