from django.urls import path

from apps.products.api import views

urlpatterns = [
    path("courses/<str:slug>/promocode/", views.PromocodeView.as_view()),
    path("courses/<str:slug>/purchase/", views.PurchaseView.as_view()),
    path("course-groups/<str:slug>/courses/", views.ProductGroupView.as_view()),
]
