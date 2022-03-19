import pytest

from chains.services import ChainSender

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def chain_sender(chain):
    return ChainSender(chain)


@pytest.fixture(autouse=True)
def send_message(mocker):
    return mocker.patch('chains.services.chain_sender.ChainSender.send')
