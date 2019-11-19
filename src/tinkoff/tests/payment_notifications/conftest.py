import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = 'testDEMO'
    settings.TINKOFF_TERMINAL_PASSWORD = 'Dfsfh56dgKl'


@pytest.fixture
def disable_token_validation(mocker):
    return mocker.patch('tinkoff.api.serializers.PaymentNotificationSerializer.validate_Token', return_value=True)
