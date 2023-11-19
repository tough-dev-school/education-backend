from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("auth/", include("apps.a12n.urls")),
    path("banking/", include("apps.banking.urls")),
    path("diplomas/", include("apps.diplomas.urls")),
    path("homework/", include("apps.homework.urls")),
    path("leads/", include("apps.magnets.urls")),
    path("notion/", include("apps.notion.urls")),
    path("orders/", include("apps.orders.urls")),
    path("studies/", include("apps.studying.urls")),
    path("users/", include("apps.users.urls")),
    path("", include("apps.products.urls")),
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
