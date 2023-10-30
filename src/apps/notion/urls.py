from django.urls import path

from apps.notion.api import views

urlpatterns = [
    path("materials/<str:page_id>/", views.NotionMaterialView.as_view()),
]
