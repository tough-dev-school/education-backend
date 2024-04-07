import pytest

from apps.dashamail.lists.dto import DashamailList

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.dashamail,
]


@pytest.fixture(autouse=True)
def update_dashamail(mocker):
    return mocker.patch("apps.dashamail.tasks.DashamailSubscriber.subscribe")


@pytest.fixture(autouse=True)
def update_dashamail_directcrm(mocker):
    return mocker.patch("apps.dashamail.tasks.directcrm_events.OrderCreated.send")


@pytest.fixture
def group(factory):
    return factory.group(dashamail_list_id=500500)


@pytest.fixture
def course(factory, group):
    return factory.course(group=group)


def test_event_is_pushed(create, user, course, update_dashamail_directcrm):
    create(user=user, item=course)

    update_dashamail_directcrm.assert_called_once()


def test_user_is_subscribed_to_the_dedicated_maillist(create, user, course, update_dashamail):
    create(user=user, item=course)

    update_dashamail.assert_called_once_with(to=DashamailList(list_id=500500))
