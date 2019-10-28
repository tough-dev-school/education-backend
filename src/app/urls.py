from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from onetime.api.views import TokenDownloadView
from users.api.views import UserView

router = routers.SimpleRouter()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v2/users/<int:pk>/', UserView.as_view()),
    path('api/v2/download/<uuid:token>/', TokenDownloadView.as_view()),
    path('api/v2/healthchecks/', include('django_healthchecks.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
