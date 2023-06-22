from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

from django.urls import include
from django.urls import path

urlpatterns = [
    path("auth/", include("a12n.urls")),
    path("banking/", include("banking.urls")),
    path("diplomas/", include("diplomas.urls")),
    path("homework/", include("homework.urls")),
    path("leads/", include("magnets.urls")),
    path("users/", include("users.urls")),
    path("notion/", include("notion.urls")),
    path("studies/", include("studying.urls")),
    path("orders/", include("orders.urls")),
    path("", include("products.urls")),
    path("healthchecks/", include("django_healthchecks.urls")),
    path(
        "docs/schema/",
        SpectacularAPIView.as_view(api_version="v2"),
        name="schema",
    ),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
    ),
]
