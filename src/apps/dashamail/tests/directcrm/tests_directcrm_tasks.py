import pytest

from apps.dashamail import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _configure_dashamail_directcrm(settings):
    settings.DASHAMAIL_DIRECTCRM_ENDPOINT = "test-endpoint"
    settings.DASHAMAIL_DIRECTCRM_SECRET_KEY = "s3cr3t"


URL = "https://directcrm.dashamail.com/v3/operations/sync?endpointId=test-endpoint&operation=OrderCreate"


def test(order, respx_mock):
    route = respx_mock.post(URL).respond(json={"status": "Success"})

    tasks.push_order_event(event_name="OrderCreated", order_id=order.pk)

    assert route.called
