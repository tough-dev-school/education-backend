import pytest

from apps.users import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def update_subscription(mocker):
    return mocker.patch("core.tasks.update_dashamail_subscription.delay")


@pytest.fixture(autouse=True)
def generate_tags(mocker):
    return mocker.patch("apps.users.tasks.generate_tags")


def test_task(user, generate_tags, update_subscription):
    tasks.rebuild_tags.delay(
        student_id=user.id,
    )

    generate_tags.assert_called_once_with(user)
    update_subscription.assert_called_once_with(
        user_id=user.pk,
    )
