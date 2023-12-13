import pytest
from httpx import Response
from apps.dashamail import exceptions
from apps.dashamail.directcrm.events import OrderCreated

pytestmark = [pytest.mark.django_db]

@pytest.fixture
def event(order):
    return OrderCreated(order=order)

@pytest.fixture(autouse=True)
def _configure_dashamail_directcrm(settings):
    settings.DASHAMAIL_DIRECTCRM_ENDPOINT = "test-endpoint"
    settings.DASHAMAIL_DIRECTCRM_SECRET_KEY = 's3cr3t'

URL="https://directcrm.dashamail.com/v3/operations/sync?endpointId=test-endpoint&operation=OrderCreate"


def test_ok(event, respx_mock):
    respx_mock.post(URL).respond(json={"status": "Success"})

    event.send()

    assert True, "event should not through anything"


def test_failure(event, respx_mock):
    respx_mock.post(URL).respond(json={"status": "Fail"})

    with pytest.raises(exceptions.DashamailDirectCRMWrongResponse):
        event.send()


def test_404(event, respx_mock):
    respx_mock.post(URL).mock(return_value=Response(401))

    with pytest.raises(exceptions.DashamailDirectCRMHTTPException):
        event.send()
