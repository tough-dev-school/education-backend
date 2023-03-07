from functools import partial
import pytest

from magnets.creator import LeadCreator


@pytest.fixture
def campaign(mixer):
    return mixer.blend("magnets.EmaiLLeadMagnetCampaign", slug="eggs")


@pytest.fixture
def creator(campaign):
    return partial(LeadCreator, campaign=campaign)
