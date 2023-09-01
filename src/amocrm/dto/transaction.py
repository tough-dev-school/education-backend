from dataclasses import dataclass

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.dto.base import AmoDTO
from orders.models import Order


@dataclass
class AmoCRMTransaction(AmoDTO):
    order: Order

    def create(self) -> int:
        """
        Create transaction for given order
        https://www.amocrm.ru/support/customers/create_purchase
        """
        response = self.http.post(
            url=f"/api/v4/customers/{self.order.user.amocrm_user.customer_id}/transactions",
            data=[
                {
                    "comment": f"Order slug in lms: {self.order.slug}",
                    "price": int(self.order.price),  # amocrm api requires field to be integer
                    "_embedded": {
                        "catalog_elements": [
                            {
                                "id": self.order.course.amocrm_course.amocrm_id,
                                "metadata": {
                                    "catalog_id": get_catalog_id(catalog_type="products"),
                                    "quantity": 1,  # only 1 course per order
                                },
                            },
                        ],
                    },
                },
            ],
        )

        return response["_embedded"]["transactions"][0]["id"]

    def delete(self) -> None:
        """
        Delete transaction for given order
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#transactions-delete
        """
        self.http.delete(
            url=f"/api/v4/customers/transactions/{self.order.amocrm_transaction.amocrm_id}",  # type: ignore
            expected_status_codes=[204],
        )
