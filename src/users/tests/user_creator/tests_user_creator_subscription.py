import pytest

from users.creator import UserCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.tasks.subscribe_to_mailjet.delay')


def test_user_is_subscribed_to_mailjet_by_default(subscribe):
    created = UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com')()

    subscribe.assert_called_once_with(created.id)


def test_not_subscribed(subscribe):
    UserCreator(name='Рулон Обоев', email='rulon.oboev@gmail.com', subscribe=False)()

    subscribe.assert_not_called()
