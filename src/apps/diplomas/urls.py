from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.diplomas.api.viewsets import DiplomaViewSet

router = SimpleRouter()

router.register("", DiplomaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
