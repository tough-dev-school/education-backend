from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers
from users.api.views import UserView

router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/users/<int:pk>/', UserView.as_view()),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
