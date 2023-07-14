import pytest

from app.integrations.dashamail.exceptions import DashamailUpdateFailed

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("tags", "request_tags"),
    [
        ([], ""),
        (["test", "TEST"], "test;TEST"),
    ],
)
def test_update_subscriber(dashamail, post, user, tags, request_tags):
    dashamail.update_subscriber(
        member_id=48,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=tags,
    )

    post.assert_called_once_with(
        url="",
        payload={
            "member_id": 48,
            "list_id": "1",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": request_tags,
            "method": "lists.update_member",
        },
    )


def test_subscription_failed(dashamail, user, fail_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com", method="POST", json=fail_response_json)

    with pytest.raises(DashamailUpdateFailed):
        dashamail.update_subscriber(
            member_id=48,
            first_name=user.first_name,
            last_name=user.last_name,
            tags=["test", "TEST"],
        )
