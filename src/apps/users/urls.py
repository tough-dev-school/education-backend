from django.urls import path

from apps.users.api.views import SelfView

urlpatterns = [
    path("me/", SelfView.as_view()),
]
