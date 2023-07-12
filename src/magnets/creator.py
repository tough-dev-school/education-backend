from dataclasses import dataclass

from app.services import BaseService
from magnets.models import EmailLeadMagnetCampaign
from magnets.models import LeadCampaignLogEntry
from users.models import User
from users.services import UserCreator


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
