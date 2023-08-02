from typing import Any

from amocrm.models import AmoCRMCourse
from amocrm.models import AmoCRMProductGroup
from amocrm.models import AmoCRMUser
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
