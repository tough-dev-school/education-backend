import pytest

from _decimal import Decimal

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def update_user_chain(mocker):
    return mocker.patch("apps.orders.services.order_creator.chain")


@pytest.fixture
def push_customer(mocker):
    return mocker.patch("apps.amocrm.tasks.push_user.si")


@pytest.fixture
def push_order(mocker):
    return mocker.patch("apps.amocrm.tasks.push_order.si")



def test_if_subscribe_and_amocrm_enabled(create, user, course, update_user_chain, push_customer, settings, push_order):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    order = create(user=user, item=course)

    update_user_chain.assert_has_calls(
        push_customer(user_id=user.id),
        push_order(order_id=order.id),
    )


def test_if_not_subscribe_and_amocrm_enabled(create, user, course, update_user_chain, push_customer, settings, push_order):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    order = create(user=user, item=course)

    update_user_chain.assert_has_calls(
        push_customer(user_id=user.id),
        push_order(order_id=order.id),
    )


def test_if_not_subscribe_and_amocrm_disabled(
    create, user, course, push_customer, push_order
):
    user.update(email="")

    create(user=user, item=course)

    push_customer.assert_not_called()
    push_order.assert_not_called()


def test_dont_call_if_free_order(create, user, course, push_customer, settings, push_order):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    create(user=user, item=course, price=Decimal(0))

    push_customer.assert_not_called()
    push_order.assert_not_called()


def test_if_not_subscribe_and_not_push_to_amocrm(
    create, user, course, push_customer, settings, push_order
):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"
    user.update(email="")

    create(user=user, item=course, push_to_amocrm=False)

    push_customer.assert_not_called()
    push_order.assert_not_called()
