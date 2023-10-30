from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from apps.diplomas.api.viewsets import DiplomaViewSet

router = SimpleRouter()

router.register("", DiplomaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
