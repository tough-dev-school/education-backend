import pytest


@pytest.fixture(autouse=True)
def campaign(mixer):
    return mixer.blend("magnets.EmailLeadMagnetCampaign", slug="eggs", success_message="No spam, only ham")
