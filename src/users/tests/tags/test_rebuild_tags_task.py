import pytest

from users import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def update_subscription(mocker):
    return mocker.patch("users.tags.tags_synchronizer.manage_users_subscription_to_dashamail")


@pytest.fixture(autouse=True)
def apply_tags(mocker):
    return mocker.patch("users.tags.tags_synchronizer.apply_tags")


def test_task(user, apply_tags, update_subscription):
    tasks.rebuild_tags.delay(
        student_id=user.id,
        list_id="1",
    )

    apply_tags.assert_called_once_with(user)
    update_subscription.assert_called_once_with(
        list_id="1",
        user=user,
        tags=user.tags,
    )
