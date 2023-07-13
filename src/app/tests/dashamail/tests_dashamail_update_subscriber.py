import pytest

from app.integrations.dashamail.exceptions import DashamailTagsUpdateFailed

pytestmark = [pytest.mark.django_db]


def test_update_subscriber(dashamail, post, user):
    dashamail.update_subscriber(
        list_id="test-list-id",
        member_id=48,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test", "TEST"],
    )

    post.assert_called_once_with(
        url="",
        payload={
            "member_id": 48,
            "list_id": "test-list-id",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": "test;TEST",
            "method": "lists.update_member",
        },
    )


def test_subscription_failed(dashamail, user, fail_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com", method="POST", json=fail_response_json)

    with pytest.raises(DashamailTagsUpdateFailed):
        dashamail.update_subscriber(
            list_id="test-list-id",
            member_id=48,
            first_name=user.first_name,
            last_name=user.last_name,
            tags=["test", "TEST"],
        )
