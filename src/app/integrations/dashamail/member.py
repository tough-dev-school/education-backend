from typing import Optional

from dataclasses import dataclass


@dataclass
class DashamailMember:
    email: str
    first_name: str
    last_name: str
    tags: Optional[list[str]] = None

    def to_dashamail(self) -> dict:
        member = {
            'email': self.email,
            'merge_1': self.first_name,
            'merge_2': self.last_name,
        }
        if self.tags:
            member['merge_3'] = ';'.join(self.tags)

        return member
