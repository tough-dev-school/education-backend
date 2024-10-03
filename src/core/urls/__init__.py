import debug_toolbar  # type: ignore
from django.conf.urls import include
from django.urls import path

from core.admin.admin_site import admin_site
from core.views import HomePageView

api = [
    path("v2/", include("core.urls.v2")),
]

urlpatterns = [
    path("api/", include(api)),
    path("admin/", admin_site.urls),
    path("__debug__/", include(debug_toolbar.urls)),
    path("", HomePageView.as_view()),
]
