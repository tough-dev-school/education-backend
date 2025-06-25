from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.lms.api.viewsets import LessonViewSet, ModuleListView

router = SimpleRouter()
router.register("lessons", LessonViewSet)
router.register("modules", ModuleListView)

urlpatterns = [
    path("", include(router.urls)),
]
