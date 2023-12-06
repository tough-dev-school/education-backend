import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def successful_response_json(successful_response_json):
    successful_response_json["response"]["data"] = [
        {
            "id": "48",
            "list_id": "1",
            "email": "test@e.mail",
            "state": "active",
        }
    ]
    return successful_response_json


def test_get_subscriber(dashamail, post, user):
    dashamail._get_member_id(
        email=user.email,
    )

    post.assert_called_once_with(
        url="",
        payload={"email": "test@e.mail", "list_id": "1", "method": "lists.get_members"},
    )


@pytest.mark.parametrize(("email", "expected_email"), [("hehe@ya.ru", "hehe@yandex.ru"), ("simple@yandex.ru", "simple@yandex.ru")])
def testwith_yandex_mail(dashamail, post, user, email, expected_email):
    user.update(email=email)

    dashamail._get_member_id(
        email=user.email,
    )

    post.assert_called_once_with(
        url="",
        payload={"email": expected_email, "list_id": "1", "method": "lists.get_members"},
    )


def testcorrect_values(dashamail, user, successful_response_json):
    dashamail.respx_mock.post(url="https://api.dashamail.com").respond(json=successful_response_json)

    member_id, is_active = dashamail._get_member_id(
        email=user.email,
    )

    assert member_id == 48
    assert is_active is True


def testerror_doesnt_exist(dashamail, user, fail_response_json):
    dashamail.respx_mock.post(url="https://api.dashamail.com").respond(json=fail_response_json)

    member_id, is_active = dashamail._get_member_id(
        email=user.email,
    )

    assert member_id is None
    assert is_active is False
