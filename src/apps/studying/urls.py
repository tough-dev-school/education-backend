from django.urls import path

from apps.studying.api import views

urlpatterns = [
    path("studies/purchased/", views.PurchasedCoursesView.as_view()),  # remove it
    path("purchased-courses/", views.PurchasedCoursesView.as_view()),
]
