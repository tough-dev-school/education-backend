from typing import final

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from apps.mailing.models import PersonalEmailDomain
from apps.users.tags.base import TagMechanism


@final
class B2BTag(TagMechanism):
    @property
    def should_be_applied(self) -> bool:
        try:
            validate_email(self.student.email)
        except ValidationError:
            return False

        personal_domains = PersonalEmailDomain.objects.all().values_list("name", flat=True)
        return self.student.email.split("@")[-1] not in personal_domains

    def get_tags_to_append(self) -> list[str]:
        return ["b2b"] if self.should_be_applied else []
