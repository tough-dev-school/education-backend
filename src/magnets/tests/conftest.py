import pytest
from functools import partial

from magnets.creator import LeadCreator


@pytest.fixture
def campaign(mixer):
    return mixer.blend('magnets.EmaiLLeadMagnetCampaign', slug='eggs')


@pytest.fixture
def creator(campaign):
    return partial(LeadCreator, campaign=campaign)
