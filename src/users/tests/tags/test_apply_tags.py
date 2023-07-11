import pytest

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_tags_append_once(user):
    apply_tags(user)
    apply_tags(user)

    assert len(user.tags) > 0
    assert len(user.tags) == len(set(user.tags))
