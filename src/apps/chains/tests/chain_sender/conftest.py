import pytest

from apps.chains.services import ChainSender

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def chain_sender(chain):
    return ChainSender(chain)


@pytest.fixture
def send_message(mocker):
    return mocker.patch("apps.chains.services.chain_sender.ChainSender.send")
