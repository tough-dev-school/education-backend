import pytest

from _decimal import Decimal

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mock_update_user_chain(mocker):
    return mocker.patch("apps.orders.services.order_creator.chain")


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.si")


@pytest.fixture
def rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.delay")


@pytest.fixture
def mock_push_customer(mocker):
    return mocker.patch("apps.amocrm.tasks.push_user.si")


@pytest.fixture
def mock_push_order(mocker):
    return mocker.patch("apps.amocrm.tasks.push_order.si")


def test_if_subscribe_and_amocrm_enabled(create, user, course, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings, mock_push_order):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    order = create(user=user, item=course)

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=user.id, subscribe=True),
        mock_push_customer(user_id=user.id),
        mock_push_order(order_id=order.id),
    )


def test_if_not_subscribe_and_amocrm_enabled(create, user, course, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings, mock_push_order):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    order = create(user=user, item=course)

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=user.id, subscribe=False),
        mock_push_customer(user_id=user.id),
        mock_push_order(order_id=order.id),
    )


def test_if_not_subscribe_and_amocrm_disabled(
    create, user, course, rebuild_tags, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings, mock_push_order
):
    user.update(email="")

    create(user=user, item=course)

    rebuild_tags.assert_called_once_with(student_id=user.id, subscribe=False)
    mock_update_user_chain.assert_not_called()
    mock_rebuild_tags.assert_not_called()
    mock_push_customer.assert_not_called()
    mock_push_order.assert_not_called()


def test_dont_call_if_free_order(create, user, course, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings, mock_push_order, rebuild_tags):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    create(user=user, item=course, price=Decimal(0))

    rebuild_tags.assert_called_once_with(student_id=user.id, subscribe=False)
    mock_update_user_chain.assert_not_called()
    mock_rebuild_tags.assert_not_called()
    mock_push_customer.assert_not_called()
    mock_push_order.assert_not_called()


def test_if_not_subscribe_and_not_push_to_amocrm(
    create, user, course, rebuild_tags, mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings, mock_push_order
):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    create(user=user, item=course, push_to_amocrm=False)

    rebuild_tags.assert_called_once_with(student_id=user.id, subscribe=False)
    mock_update_user_chain.assert_not_called()
    mock_rebuild_tags.assert_not_called()
    mock_push_customer.assert_not_called()
    mock_push_order.assert_not_called()
