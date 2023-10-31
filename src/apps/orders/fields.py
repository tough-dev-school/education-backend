from typing import Any

from core.models import models


class ItemField(models.ForeignKey):
    """This is a simple replacement for the ContentType framework -- fields of this type
    are fields linked to items
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._is_item = True
        super().__init__(*args, **kwargs)


class UnknownItemException(Exception):
    pass
