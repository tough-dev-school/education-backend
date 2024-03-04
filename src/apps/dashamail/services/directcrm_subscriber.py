from dataclasses import dataclass

from apps.dashamail.lists.dto import DashamailList, DashamailSubscriber
from apps.products.models import Course
from apps.users.models import User
from core.services import BaseService


@dataclass
class DashamailDirectCRMSubscriber(BaseService):
    """Subscribe user to the dedicated per-product directcrm mailing list"""

    user: User
    product: Course

    def act(self) -> None:
        subscriber = DashamailSubscriber(user=self.user)

        subscriber.subscribe(to=self.get_mail_list())

    def get_mail_list(self) -> DashamailList:
        return self.get_mail_list_by_product() or self.create_mail_list()

    def get_mail_list_by_product(self) -> DashamailList | None:
        if self.product.group.dashamail_list_id is not None:
            return DashamailList(list_id=self.product.group.dashamail_list_id)

    def create_mail_list(self) -> DashamailList:
        list_id = DashamailList(name=self.product.group.name).create()

        self.product.group.dashamail_list_id = list_id
        self.product.group.save(update_fields=["modified", "dashamail_list_id"])

        return DashamailList(list_id=list_id)
