from enum import IntEnum


class AmoCRMTaskType(IntEnum):
    """Look for `task_type` at https://www.amocrm.ru/developers/content/crm_platform/tasks-api#common-info"""

    CONTACT = 1
    MEETING = 2
