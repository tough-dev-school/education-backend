from enum import IntEnum
from typing import NamedTuple


class CatalogField(NamedTuple):
    """Represents amocrm's custom catalog field that could be used with various entities

    https://www.amocrm.ru/developers/content/crm_platform/custom-fields
    """

    id: int
    code: str


class Catalog(NamedTuple):
    """Represents amocrm's catalog aka 'список'

    https://www.amocrm.ru/developers/content/crm_platform/catalogs-api#lists-list
    """

    id: int
    name: str
    type: str


class TaskType(IntEnum):
    """Represents type of amocrm's task.

    Look for `task_type` at https://www.amocrm.ru/developers/content/crm_platform/tasks-api#common-info
    """

    CONTACT = 1
    MEETING = 2


class Task(NamedTuple):
    """Represents amocrm's Taks

    Only fields that are used in the app are listed.
    https://www.amocrm.ru/developers/content/crm_platform/tasks-api#tasks-list
    """

    id: int
    task_type_id: TaskType
    is_completed: bool
    text: str
