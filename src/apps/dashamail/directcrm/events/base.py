from abc import ABCMeta, abstractmethod, abstractproperty
from decimal import Decimal

import httpx
from django.conf import settings

from apps.dashamail import exceptions


class Event(metaclass=ABCMeta):
    """Dashamail DirectCRM backend event

    https://lk.dashamail.ru/?page=cdp&action=developer
    """

    @abstractproperty
    def name(self) -> str:
        """Event name"""

    @abstractmethod
    def to_json(self) -> dict[str, str | dict]:
        """Actual event payload, 'data' field in the dashamail request"""

    @staticmethod
    def format_price(price: Decimal) -> str:
        return str(price).replace(".", ",")

    def send(self) -> None:
        response = httpx.post(
            url=f"https://directcrm.dashamail.com/v3/operations/sync?endpointId={settings.DASHAMAIL_DIRECTCRM_ENDPOINT}&operation={self.name}",
            json=self.to_json(),
            headers={
                "Authorization": f"Dashamail secretKey={settings.DASHAMAIL_DIRECTCRM_SECRET_KEY}",
            },
        )

        if response.status_code != 200:
            raise exceptions.DashamailDirectCRMHTTPException(f"Wrong HTTP response from dashamail directcrm: {response.status_code}")

        response_json = response.json()

        if response_json is None or response_json["status"] != "Success":
            raise exceptions.DashamailDirectCRMWrongResponse(f"Wrong response from dashamail directcrm: {response_json}")
