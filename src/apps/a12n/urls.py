from dj_rest_auth.views import PasswordChangeView as DjRestAuthPasswordChangeView
from dj_rest_auth.views import PasswordResetConfirmView as DjRestAuthPasswordResetConfirmView

from django.urls import path

from apps.a12n.api.views import ObtainJSONWebTokenViaPasswordlessToken
from apps.a12n.api.views import ObtainJSONWebTokenViaUserId
from apps.a12n.api.views import ObtainJSONWebTokenView
from apps.a12n.api.views import RefreshJSONWebTokenView
from apps.a12n.api.views import RequestPasswordLessToken
from apps.a12n.api.views import RequestPasswordResetView

urlpatterns = [
    path("token/", ObtainJSONWebTokenView.as_view()),
    path("token/refresh/", RefreshJSONWebTokenView.as_view()),
    path("password/reset/", RequestPasswordResetView.as_view()),
    path("password/reset/confirm/", DjRestAuthPasswordResetConfirmView.as_view()),
    path("password/change/", DjRestAuthPasswordChangeView.as_view()),
    path("passwordless-token/request/<str:user_email>/", RequestPasswordLessToken.as_view()),
    path("passwordless-token/<uuid:token>/", ObtainJSONWebTokenViaPasswordlessToken.as_view()),
    path("as/<int:user_id>/", ObtainJSONWebTokenViaUserId.as_view()),
]
