import pytest

from magnets.models import LeadCampaignLogEntry
from users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def rebuild_tags(mocker):
    return mocker.patch("users.services.user_creator.rebuild_tags.delay")


@pytest.fixture
def execute(mocker):
    return mocker.patch("magnets.models.EmailLeadMagnetCampaign.execute")


def get_user():
    return User.objects.last()


def get_log_entry():
    return LeadCampaignLogEntry.objects.last()


def test(creator):
    creator(name="Фёдор Шаляпин", email="support@m1crosoft.com")()

    created = get_user()

    assert created.email == "support@m1crosoft.com"
    assert created.first_name == "Фёдор"
    assert created.last_name == "Шаляпин"


def test_nameless(creator):
    creator(email="support@m1crosoft.com")()

    created = get_user()

    assert created.email == "support@m1crosoft.com"
    assert created.first_name == ""
    assert created.last_name == ""


def test_existing_user(creator, mixer):
    user = mixer.blend(User, first_name="Фёдор", last_name="Шаляпин", email="support@m1crosoft.com")
    creator(name="Фёдор Шаляпин", email="support@m1crosoft.com")()

    user.refresh_from_db()

    assert get_user() == user


def test_user_is_subscribed_with_tags(creator, mixer, rebuild_tags):
    user = mixer.blend(User, first_name="Фёдор", last_name="Шаляпин", email="support@m1crosoft.com")
    creator(name="r00t", email="support@m1crosoft.com")()

    rebuild_tags.assert_called_once_with(user.id)


def test_log_entry_is_created(creator, campaign):
    creator(name="Фёдор Шаляпин", email="support@m1crosoft.com")()

    log_entry = get_log_entry()

    assert log_entry.campaign == campaign
    assert log_entry.user == get_user()  # created user


def test_campaign_is_executed(creator, mixer, execute):
    user = mixer.blend(User, first_name="Фёдор", last_name="Шаляпин", email="support@m1crosoft.com")

    creator(name="Фёдор Шаляпин", email="support@m1crosoft.com")()

    execute.assert_called_once_with(user)
