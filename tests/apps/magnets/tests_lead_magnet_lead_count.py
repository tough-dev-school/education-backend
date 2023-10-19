import pytest

from apps.magnets.models import EmailLeadMagnetCampaign

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("campaign"),
]


def get_annotated_campaign():
    return EmailLeadMagnetCampaign.objects.with_lead_count().filter(slug="eggs").first()


@pytest.fixture
def another_campaign(mixer):
    return mixer.blend("magnets.EmailLeadMagnetCampaign")


def test_zero():
    campaign = get_annotated_campaign()

    assert campaign.lead_count == 0


def test_two(mixer, campaign):
    mixer.cycle(2).blend("magnets.LeadCampaignLogEntry", campaign=campaign)

    campaign = get_annotated_campaign()

    assert campaign.lead_count == 2


def test_another_campaign(mixer, another_campaign):
    mixer.cycle(2).blend("magnets.LeadCampaignLogEntry", campaign=another_campaign)

    campaign = get_annotated_campaign()

    assert campaign.lead_count == 0
