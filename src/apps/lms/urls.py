from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.lms.api.viewsets import LessonViewSet, ModuleViewSet

router = SimpleRouter()
router.register("lessons", LessonViewSet)
router.register("modules", ModuleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
