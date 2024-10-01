from typing import Any

from django.contrib import admin

class AdminSite(admin.AdminSite):

    def __init__(self, *args, **kwargs):
        super(AdminSite, self).__init__(*args, **kwargs)
        self._registry.update(admin.site._registry)

    def get_app_list(self, request: Any, app_label=None) -> list[Any]:
        app_list = super().get_app_list(request, app_label)
        app_order = ['orders', 'notion', 'chains', 'products', 'otherapp']
        app_list.sort(key=lambda x: app_order.index(x['app_label']) if x['app_label'] in app_order else len(app_order))

        print(app_list)
        return app_list
    
admin_site = AdminSite(name='custom_admin')
