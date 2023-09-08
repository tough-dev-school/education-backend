import pytest

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("tags", "request_tags"),
    [
        ([], ""),
        (["test", "TEST"], "test;TEST"),
    ],
)
def test_subscribe(dashamail, post, user, tags, request_tags):
    dashamail.subscribe_user(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=tags,
    )

    post.assert_called_once_with(
        url="",
        payload={
            "email": "test@e.mail",
            "list_id": "1",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": request_tags,
            "method": "lists.add_member",
        },
    )


def test_subscription_failed(dashamail, user, fail_response_json):
    dashamail.respx_mock.post(url="https://api.dashamail.com").respond(json=fail_response_json)

    with pytest.raises(DashamailSubscriptionFailed):
        dashamail.subscribe_user(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            tags=["test", "TEST"],
        )
