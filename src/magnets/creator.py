from magnets.models import EmailLeadMagnetCampaign, LeadCampaignLogEntry
from users.models import User
from users.services import UserCreator


class LeadCreator:
    def __init__(self, campaign: EmailLeadMagnetCampaign, email: str, name: str = None):
        self.data = {
            'name': name,
            'email': email,
        }

        self.campaign = campaign

    def __call__(self):
        self.user = self._create_user()
        self._create_log_entry()

        self.campaign.execute(self.user)

    def _create_user(self) -> User:
        return UserCreator(
            name=self.data['name'],
            email=self.data['email'],
            subscribe=True,
            tags=self.tags,
        )()

    def _create_log_entry(self):
        LeadCampaignLogEntry.objects.create(
            user=self.user,
            campaign=self.campaign,
        )

    @property
    def tags(self):
        return [f'{self.campaign.slug}-lead-magnet']
