from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from decimal import Decimal


class Event(metaclass=ABCMeta):
    @abstractproperty
    def name(self) -> str:
        """Event name"""

    @abstractmethod
    def to_json(self) -> dict[str, str | dict]:
        """Actual event payload, 'data' field in the dashamail request"""

    def to_payload(self) -> dict[str, str | dict]:
        return {
            "operation": self.name,
            "data": self.to_json(),
        }

    @staticmethod
    def format_price(price: Decimal) -> str:
        return str(price)
