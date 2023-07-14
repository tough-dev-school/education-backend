import pytest

from users.services import UserCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.delay")


def test_user_is_not_subscribed_to_dashamail_by_default(rebuild_tags):
    UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com")()

    rebuild_tags.assert_not_called()


def test_tags_are_passed(rebuild_tags):
    created = UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com", subscribe=True)()

    rebuild_tags.assert_called_once_with(created.id)


def test_not_subscribed(rebuild_tags):
    UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com", subscribe=False)()

    rebuild_tags.assert_not_called()


@pytest.mark.parametrize("wants_to_subscribe", [True, False])
def test_storing_wants_to_subscribe_flag(wants_to_subscribe):
    created = UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com", subscribe=wants_to_subscribe)()

    created.refresh_from_db()

    assert created.subscribed is wants_to_subscribe
