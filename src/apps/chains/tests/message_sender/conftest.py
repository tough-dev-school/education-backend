import pytest

from apps.chains.services import MessageSender

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def message_sender():
    return MessageSender


@pytest.fixture(autouse=True)
def owl(mocker):
    return mocker.patch("apps.mailing.tasks.Owl")
