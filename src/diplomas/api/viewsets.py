
from rest_framework.exceptions import MethodNotAllowed

from app.viewsets import AppViewSet
from diplomas.api import serializers
from diplomas.api.permissions import DiplomaPermission
from diplomas.models import Diploma


class DiplomaViewSet(AppViewSet):
    queryset = Diploma.objects.for_viewset()
    lookup_field = 'slug'
    serializer_class = serializers.DiplomaSerializer
    serializer_action_classes = {
        'create': serializers.DiplomaCreateSerializer,
        'retrieve': serializers.DiplomaRetrieveSerializer,
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
