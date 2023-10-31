from django.urls import path

from apps.users.api import views

urlpatterns = [
    path("me/", views.SelfView.as_view()),
    path("", views.UserView.as_view()),
]
