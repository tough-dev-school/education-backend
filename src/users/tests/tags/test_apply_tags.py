import pytest

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_correct_subscribes_to_dashamail(user, mock_subscribe_to_dashamail):
    apply_tags(user)

    user.refresh_from_db()
    assert len(user.tags) > 0
    mock_subscribe_to_dashamail.assert_called_once_with(user=user, tags=user.tags)
