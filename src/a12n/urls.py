from django.urls import path

from a12n.api.views import (
    ObtainJSONWebTokenViaPasswordlessToken, ObtainJSONWebTokenViaUserId, ObtainJSONWebTokenView,
    RefreshJSONWebTokenView, RequestPasswordLessToken)

urlpatterns = [
    path('token/', ObtainJSONWebTokenView.as_view()),
    path('token/refresh/', RefreshJSONWebTokenView.as_view()),
    path('passwordless-token/request/<str:user_email>/', RequestPasswordLessToken.as_view()),
    path('passwordless-token/<uuid:token>/', ObtainJSONWebTokenViaPasswordlessToken.as_view()),
    path('as/<int:user_id>/', ObtainJSONWebTokenViaUserId.as_view()),
]
