import pytest

from apps.dashamail.lists.dto import DashamailList, DashamailSubscriber

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.dashamail,
]


@pytest.fixture
def nonexistant_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.get_member_id", return_value=None)


@pytest.fixture
def subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.get_member_id", return_value=1337)


@pytest.fixture
def dashamail_api(mocker):
    return mocker.patch(
        "apps.dashamail.lists.http.DashamailListsHTTP.call",
        return_value={
            "response": {
                "msg": {
                    "err_code": 0,
                },
            },
        },
    )


@pytest.mark.usefixtures("subscriber")
def test_user_is_updated_when_he_exists(dashamail_api, user):
    DashamailSubscriber(user).subscribe()

    dashamail_api.assert_called_once_with(
        "lists.update_member",
        dict(
            list_id="1",
            member_id="1337",
            merge_1=user.first_name,
            merge_2=user.last_name,
            merge_3="popug-3-self__purchased;any-purchase",
        ),
    )


@pytest.mark.usefixtures("nonexistant_subscriber")
@pytest.mark.parametrize(
    ["email", "expected"],
    [
        ("test@e.mail", "test@e.mail"),
        ("hehe@ya.ru", "hehe@yandex.ru"),  # validate email converion
        ("hehe@yandex.ru", "hehe@yandex.ru"),
    ],
)
def test_user_gets_subscribed_when_he_didnt_exist(dashamail_api, user, email, expected):
    user.email = email
    DashamailSubscriber(user).subscribe()

    dashamail_api.assert_called_once_with(
        "lists.add_member",
        dict(
            list_id="1",
            email=expected,
            merge_1=user.first_name,
            merge_2=user.last_name,
            merge_3="popug-3-self__purchased;any-purchase",
        ),
    )


@pytest.mark.usefixtures("nonexistant_subscriber")
def test_custom_list_id(dashamail_api, user):
    DashamailSubscriber(user).subscribe(to=DashamailList(list_id=200500))

    dashamail_api.assert_called_once_with(
        "lists.add_member",
        dict(
            list_id="200500",
            email="test@e.mail",
            merge_1=user.first_name,
            merge_2=user.last_name,
            merge_3="popug-3-self__purchased;any-purchase",
        ),
    )
