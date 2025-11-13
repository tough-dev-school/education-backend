from django.urls import path

from apps.notion.api import views

urlpatterns = [
    path("notion/materials/<str:page_id>/", views.LegacyNotionMaterialView.as_view()),
    path("materials/<str:page_id>/", views.MaterialView.as_view()),
    path("materials/<str:page_id>/status/", views.MaterialStatusView.as_view()),
    path("materials/<str:page_id>/update/", views.MaterialUpdateView.as_view()),
]
