from amocrm.dto import AmoCRMGroup
from app.services import BaseService
from products.models import Group


class AmoCRMGroupsPusher(BaseService):
    """
    Push all Groups to AmoCRM as ENUM options field for product
    it's necessary to save amocrm_id for ProductGroups,
    if not - next updating will set new field options with new ids but same values
    which will break consistency
    """

    def act(self) -> None:
        pushed_groups = self.push_all_groups()

        for group_slug, amocrm_id in pushed_groups:
            Group.objects.filter(slug=group_slug).update(amocrm_id=amocrm_id)

    @staticmethod
    def push_all_groups() -> list[tuple[str, int]]:
        groups_to_push = Group.objects.all()
        return AmoCRMGroup(groups=groups_to_push).push()
