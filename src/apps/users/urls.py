from django.urls import path

from apps.users.api import views

urlpatterns = [
    path("", views.UserListView.as_view()),
    path("me/", views.SelfView.as_view()),
]
