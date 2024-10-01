from typing import Any

from django.contrib import admin
from django.http.request import HttpRequest


class AdminSite(admin.AdminSite):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self._registry.update(admin.site._registry)

    def get_app_list(self, request: HttpRequest, app_label: str | None = None) -> list[str]:
        app_list = super().get_app_list(request, app_label)
        app_list.sort(key=self._get_app_order_index)
        return app_list

    def _get_app_order_index(self, element: Any) -> int:
        app_order = ["orders", "notion", "chains", "products", "otherapp"]

        if element["app_label"] in app_order:
            return app_order.index(element["app_label"])

        return len(app_order)


admin_site = AdminSite(name="custom_admin")
