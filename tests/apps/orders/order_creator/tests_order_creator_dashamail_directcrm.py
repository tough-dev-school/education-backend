import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.dashamail,
]

@pytest.fixture(autouse=True)
def update_dashamail(mocker):
    return mocker.patch("apps.dashamail.tasks.DashamailListsClient.subscribe_or_update")

@pytest.fixture(autouse=True)
def update_dashamail_directcrm(mocker):
    return mocker.patch("apps.dashamail.tasks.directcrm_events.OrderCreated.send")


def test(create,user, course, update_dashamail_directcrm):
    create(user=user, item=course)

    update_dashamail_directcrm.assert_called_once()
