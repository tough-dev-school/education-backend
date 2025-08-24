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
    create(user=user, item=course, subscribe=True)

    update_dashamail_directcrm.assert_called_once()


def test_event_is_not_pushed_when_dashamail_is_disabled(create, user, course, update_dashamail_directcrm, update_dashamail, settings):
    settings.DASHAMAIL_API_KEY = ""

    create(user=user, item=course)

    update_dashamail_directcrm.assert_not_called()
    update_dashamail.assert_not_called()


def test_user_is_subscribed_to_the_dedicated_maillist(create, user, course, update_dashamail, mocker):
    create(user=user, item=course, subscribe=True)

    update_dashamail.assert_has_calls(
        [
            mocker.call(),  # common maillistr
            mocker.call(to=DashamailList(list_id=500500)),  # particular course maillist
        ]
    )


def test_user_is_not_subscribed_if_dashamail_is_disabled(create, user, course, update_dashamail, settings):
    settings.DASHAMAIL_API_KEY = ""

    create(user=user, item=course, subscribe=True)

    update_dashamail.assert_not_called()
