from dataclasses import dataclass

from apps.magnets.models import EmailLeadMagnetCampaign, LeadCampaignLogEntry
from apps.users.models import User
from apps.users.services import UserCreator
from core.services import BaseService


@dataclass
class LeadCreator(BaseService):
    campaign: EmailLeadMagnetCampaign
    email: str
    name: str | None = None

    def __post_init__(self) -> None:
        self.data = {
            "name": self.name or "",
            "email": self.email,
        }

    def act(self) -> None:
        user = self._create_user()
        self._create_log_entry(user)

        self.campaign.execute(user)

    def _create_user(self) -> User:
        return UserCreator(
            name=self.data["name"],
            email=self.data["email"],
            subscribe=True,
        )()

    def _create_log_entry(self, user: User) -> None:
        LeadCampaignLogEntry.objects.create(
            user=user,
            campaign=self.campaign,
        )
