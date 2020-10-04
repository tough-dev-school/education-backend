from magnets.models import EmailLeadMagnetCampaign
from users.creator import UserCreator
from users.models import User


class LeadCreator:
    def __init__(self, name: str, email: str, campaign: EmailLeadMagnetCampaign):
        self.data = {
            'name': name,
            'email': email,
        }

        self.campaign = campaign

    def __call__(self):
        self.user = self._create_user()

    def _create_user(self) -> User:
        return UserCreator(
            name=self.data['name'],
            email=self.data['email'],
            subscribe=True,
        )()
