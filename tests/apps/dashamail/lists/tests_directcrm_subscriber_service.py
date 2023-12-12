import pytest
from unittest.mock import call
from apps.dashamail.services import DashamailDirectCRMSubscriber

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.dashamail,
]


@pytest.fixture
def group(factory):
    return factory.group(name="Асинхронный аналих", dashamail_list_id=None)


@pytest.fixture
def course(factory, group):
    return factory.course(group=group)


@pytest.fixture(autouse=True)
def dashamail_api(mocker):
    return mocker.patch("apps.dashamail.lists.http.DashamailListsHTTP.call", return_value={
        "response": {
            "msg": {
                "err_code": 0,
            },
            "data": {
                "list_id": 300500,
            },
        },
    })

@pytest.fixture
def nonexistant_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.get_member_id", return_value=None)

@pytest.fixture
def subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.get_member_id", return_value=1337)


@pytest.mark.usefixtures('nonexistant_subscriber')
def test_creating_list(dashamail_api, user, course, mocker):
    DashamailDirectCRMSubscriber(user=user, product=course)()

    assert dashamail_api.call_args_list[0] == mocker.call(
        "lists.add", {"name": "Асинхронный аналих"},
    )

    assert dashamail_api.call_args_list[1] == mocker.call(
        "lists.add_member", {
            "list_id": "300500",
            "email": "test@e.mail",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": "popug-3-self__purchased;any-purchase",
        })


@pytest.mark.usefixtures('nonexistant_subscriber')
def test_creating_list_updates_product_group(user, course):
    DashamailDirectCRMSubscriber(user=user, product=course)()

    course.group.refresh_from_db()

    assert course.group.dashamail_list_id == 300500


@pytest.mark.usefixtures('nonexistant_subscriber')
def test_existing_list(dashamail_api, user, course):
    course.group.update(dashamail_list_id=200500)

    DashamailDirectCRMSubscriber(user=user, product=course)()

    dashamail_api.assert_called_once_with(
        "lists.add_member", {
            "list_id": "200500",
            "email": "test@e.mail",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": "popug-3-self__purchased;any-purchase",
        })


@pytest.mark.usefixtures('subscriber')
def test_existing_subscriber(dashamail_api, user, course):
    course.group.update(dashamail_list_id=200500)

    DashamailDirectCRMSubscriber(user=user, product=course)()

    dashamail_api.assert_called_once_with(
        "lists.update_member", {
            "list_id": "200500",
            "member_id": "1337",
            "merge_1": "Rulon",
            "merge_2": "Oboev",
            "merge_3": "popug-3-self__purchased;any-purchase",
        })
