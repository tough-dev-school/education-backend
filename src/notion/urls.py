from django.urls import path

from notion.api import views

urlpatterns = [
    path('<str:page_id>/', views.NotionPageView.as_view()),
]
