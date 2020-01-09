import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.tasks.subscribe_to_mailjet.delay')


def test_user_is_subscribed_to_mailjet_by_default(subscribe, settings):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com')()

    subscribe.assert_called_once_with(user_id=created.id, list_id=settings.MAILJET_LIST_ID_WHERE_ALL_CONTACTS_ARE_STORED)


def test_not_subscribed(subscribe):
    UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', subscribe=False)()

    subscribe.assert_not_called()


@pytest.mark.parametrize('wants_to_subscribe', [True, False])
def test_storing_wants_to_subscribe_flag(wants_to_subscribe):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', subscribe=wants_to_subscribe)()

    created.refresh_from_db()

    assert created.subscribed is wants_to_subscribe
