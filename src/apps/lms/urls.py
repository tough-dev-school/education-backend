from django.urls import include, path
from rest_framework.routers import SimpleRouter

from apps.lms.api.views import ModuleListView
from apps.lms.api.viewsets import LessonViewSet

router = SimpleRouter()
router.register("lessons", LessonViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("modules/", ModuleListView.as_view()),
]
