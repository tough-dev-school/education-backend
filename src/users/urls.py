from rest_framework.routers import SimpleRouter

from django.urls import include
from django.urls import path

from users.api import views

router = SimpleRouter()
router.register("", views.CourseStudentsViewSet, basename="course-students")

urlpatterns = [
    path("me/", views.SelfView.as_view()),
    path("", include(router.urls)),
]
