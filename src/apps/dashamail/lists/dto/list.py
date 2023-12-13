from dataclasses import dataclass

from apps.dashamail.lists.dto.base import DashamailListsDTO


@dataclass
class DashamailList(DashamailListsDTO):
    list_id: int | None = None
    name: str | None = None

    def create(self) -> int:
        if self.name is None:
            raise RuntimeError("List name must be given")

        response = self.api.call("lists.add", {"name": self.name})

        return response["response"]["data"]["list_id"]
