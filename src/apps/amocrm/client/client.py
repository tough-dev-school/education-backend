from apps.amocrm.client import http


class AmoCRMClient:
    """
    Client to deal with amoCRM with auto tokens refresh.
    """

    def enable_customers(self) -> None:
        """Enable customers list is required to create/update customers"""
        http.patch(url="/api/v4/customers/mode", data={"mode": "segments", "is_enabled": True})
