from amocrm.dto import AmoCRMGroups
from amocrm.models import AmoCRMProductGroup
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
        self.save_new_groups_ids(pushed_groups=pushed_groups)

    @staticmethod
    def push_all_groups() -> list[tuple[str, int]]:
        groups_to_push = Group.objects.all()
        return AmoCRMGroups(groups=groups_to_push).push()

    @staticmethod
    def save_new_groups_ids(pushed_groups: list[tuple[str, int]]) -> None:
        for group_slug, amocrm_id in pushed_groups:
            AmoCRMProductGroup.objects.get_or_create(
                amocrm_id=amocrm_id,
                group=Group.objects.get(slug=group_slug),
            )
