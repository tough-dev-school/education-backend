from amocrm.dto import AmoCRMGroup
from amocrm.models import AmoCRMProductGroup
from app.services import BaseService
from products.models import Group


class AmoCRMGroupPusher(BaseService):
    """
    Push all Groups to AmoCRM as ENUM options field for product
    it's necessary to save amocrm_id for ProductGroups,
    if not - next updating will set new field options with new ids but same values
    which will break consistency
    """

    def act(self) -> None:
        groups = Group.objects.all()
        groups_with_amocrm_id = AmoCRMGroup(groups=groups).push()
        self.save_amocrm_groups(groups_with_amocrm_id=groups_with_amocrm_id)

    @staticmethod
    def save_amocrm_groups(groups_with_amocrm_id: dict) -> None:
        for group_slug, amocrm_id in groups_with_amocrm_id.items():
            group = Group.objects.get(slug=group_slug)
            if not hasattr(group, "amocrm_group"):
                AmoCRMProductGroup.objects.create(group=group, amocrm_id=amocrm_id)
