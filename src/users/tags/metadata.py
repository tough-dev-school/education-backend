from dataclasses import dataclass
from dataclasses import field

from users.models import User


@dataclass
class TagSetterMetadata:
    """Used for communicate between tags in the pipeline"""

    user: User
    applied_tags: list[str] = field(default_factory=list)
