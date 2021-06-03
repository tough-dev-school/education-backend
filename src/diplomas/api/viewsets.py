
from app.viewsets import AppViewSet
from diplomas.api.permissions import DiplomaPermission
from diplomas.api.serializers import DiplomaSerializer
from diplomas.models import Diploma


class DiplomaViewSet(AppViewSet):
    queryset = Diploma.objects.for_viewset()
    lookup_field = 'slug'
    serializer_class = DiplomaSerializer
    permission_classes = [DiplomaPermission]

    def get_queryset(self):
        """Filter diplomas only for current user"""
        queryset = super().get_queryset()

        if self.action != 'retrieve' and not self.request.user.has_perm('diplomas.access_all_diplomas'):
            queryset = queryset.for_user(self.request.user)

        return queryset
