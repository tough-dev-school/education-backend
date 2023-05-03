from django.urls import path

from studying.api import views

urlpatterns = [
    path("purchased/", views.PurchasedCoursesView.as_view()),
]
