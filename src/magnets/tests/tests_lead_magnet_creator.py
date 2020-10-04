from functools import partial

import pytest

from magnets.creator import LeadCreator
from magnets.models import LeadCampaignLogEntry
from users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def campaign(mixer):
    return mixer.blend('magnets.EmaiLLeadMagnetCampaign')


@pytest.fixture
def creator(campaign):
    return partial(LeadCreator, campaign=campaign)


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.tasks.subscribe_to_mailchimp.delay')


def get_user():
    return User.objects.last()


def get_log_entry():
    return LeadCampaignLogEntry.objects.last()


def test(creator):
    creator(name='Фёдор Шаляпин', email='support@m1crosoft.com')()

    created = get_user()

    assert created.email == 'support@m1crosoft.com'
    assert created.first_name == 'Фёдор'
    assert created.last_name == 'Шаляпин'


def test_user_is_subscribed(creator, subscribe):
    creator(name='r00t', email='support@m1crosoft.com')()

    subscribe.assert_called_once()


def test_existing_user(creator, mixer):
    user = mixer.blend(User, first_name='Фёдор', last_name='Шаляпин', email='support@m1crosoft.com')
    creator(name='Фёдор Шаляпин', email='support@m1crosoft.com')()

    user.refresh_from_db()

    assert get_user() == user


def test_log_entry_is_created(creator, campaign):
    creator(name='Фёдор Шаляпин', email='support@m1crosoft.com')()

    log_entry = get_log_entry()

    assert log_entry.campaign == campaign
    assert log_entry.user == get_user()  # created user
