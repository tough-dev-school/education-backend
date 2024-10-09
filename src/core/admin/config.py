from django.contrib.admin.apps import AdminConfig


class AdminConfig(AdminConfig):
    default_site = "core.admin.admin_site.AdminSite"
