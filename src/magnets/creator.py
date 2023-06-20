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

    def __post_init__(self):
        self.data = {
            "name": self.name or "",
            "email": self.email,
        }

    def act(self):
        user = self._create_user()
        self._create_log_entry(user)

        self.campaign.execute(user)

    def _create_user(self) -> User:
        return UserCreator(
            name=self.data["name"],
            email=self.data["email"],
            subscribe=True,
            tags=self.tags,
        )()

    def _create_log_entry(self, user: User):
        LeadCampaignLogEntry.objects.create(
            user=user,
            campaign=self.campaign,
        )

    @property
    def tags(self):
        return [f"{self.campaign.slug}-lead-magnet"]
