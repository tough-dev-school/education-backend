import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = 'testDEMO'
    settings.TINKOFF_TERMINAL_PASSWORD = 'Dfsfh56dgKl'


@pytest.fixture
def _disable_token_validation(mocker):
    mocker.patch('tinkoff.api.serializers.PaymentNotificationSerializer.validate_Token', return_value=True)
