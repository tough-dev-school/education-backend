from typing import Any

from amocrm.models import AmoCRMCourse
from amocrm.models import AmoCRMOrderLead
from amocrm.models import AmoCRMOrderTransaction
from amocrm.models import AmoCRMProductGroup
from amocrm.models import AmoCRMUser
from amocrm.models import AmoCRMUserContact
from app.test.factory import register


@register
def amocrm_user(self: Any, **kwargs: Any) -> AmoCRMUser:
    return self.mixer.blend("amocrm.AmoCRMUser", **kwargs)


@register
def amocrm_group(self: Any, **kwargs: Any) -> AmoCRMProductGroup:
    return self.mixer.blend("amocrm.AmoCRMProductGroup", **kwargs)


@register
def amocrm_course(self: Any, **kwargs: Any) -> AmoCRMCourse:
    return self.mixer.blend("amocrm.AmoCRMCourse", **kwargs)


@register
def amocrm_user_contact(self: Any, **kwargs: Any) -> AmoCRMUserContact:
    return self.mixer.blend("amocrm.AmoCRMUserContact", **kwargs)


@register
def amocrm_order_transaction(self: Any, **kwargs: Any) -> AmoCRMOrderTransaction:
    return self.mixer.blend("amocrm.AmoCRMOrderTransaction", **kwargs)


@register
def amocrm_order_lead(self: Any, **kwargs: Any) -> AmoCRMOrderLead:
    return self.mixer.blend("amocrm.AmoCRMOrderLead", **kwargs)
