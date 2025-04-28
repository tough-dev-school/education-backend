from copy import copy

from django.conf import settings
from django.contrib import admin
from django.http.request import HttpRequest


class AdminSite(admin.AdminSite):
    def get_app_list(self, request: HttpRequest, app_label: str | None = None) -> list[dict]:
        """Adds custom ordering and ability to hiden particular models from the app list"""
        app_list = super().get_app_list(request, app_label)

        app_list = self.sort(app_list)
        app_list = self.remove_hidden_models(app_list)

        return app_list

    @staticmethod
    def remove_hidden_models(app_list: list) -> list:
        apps = copy(app_list)
        for app_id, app in enumerate(apps):
            for model_id, model in enumerate(app["models"]):
                label = str(model["model"]._meta)
                if label.lower() in [label.lower() for label in settings.ADMIN_HIDDEN_MODELS]:
                    del apps[app_id]["models"][model_id]

        return apps

    @staticmethod
    def sort(app_list: list) -> list:
        def sort_key(app: dict) -> int:
            if app["app_label"] in settings.ADMIN_APP_ORDER:
                return settings.ADMIN_APP_ORDER.index(app["app_label"])

            return len(settings.ADMIN_APP_ORDER)

        apps = copy(app_list)

        apps.sort(key=sort_key)

        return apps


__all__ = ["AdminSite"]
