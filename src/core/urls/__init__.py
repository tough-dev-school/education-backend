import debug_toolbar  # type: ignore
from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from core.views import HomePageView

api = [
    path("v2/", include("core.urls.v2")),
]

urlpatterns = [
    path("api/", include(api)),
    path("admin/", admin.site.urls),
    # path('silk/', include('silk.urls', namespace='silk')),  # NOQA: ERA001
    path("__debug__/", include(debug_toolbar.urls)),
    path("", HomePageView.as_view()),
]
