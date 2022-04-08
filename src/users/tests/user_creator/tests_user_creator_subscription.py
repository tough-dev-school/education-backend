import pytest

from users.services import UserCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('users.services.user_creator.subscribe_user_to_dashamail')


def test_user_is_subscribed_to_dashamail_by_default(subscribe):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com')()

    subscribe.assert_called_once_with(
        user=created,
        tags=None,
    )


def test_tags_are_passed(subscribe):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', tags=['aatag', 'bbtag'])()

    subscribe.assert_called_once_with(
        user=created,
        tags=['aatag', 'bbtag'],
    )


def test_not_subscribed(subscribe):
    UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', subscribe=False)()

    subscribe.assert_not_called()


@pytest.mark.parametrize('wants_to_subscribe', [True, False])
def test_storing_wants_to_subscribe_flag(wants_to_subscribe):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', subscribe=wants_to_subscribe)()

    created.refresh_from_db()

    assert created.subscribed is wants_to_subscribe
