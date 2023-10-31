import pytest

pytestmark = [pytest.mark.django_db]


def test_user_is_changed(email_changer, user, order):
    changer = email_changer(order, email=user.email)

    changer()
    order.refresh_from_db()

    assert order.user == user
    assert order.user.first_name == "Kamaz"
    assert order.user.last_name == "Otkhodov"


def test_initial_user_name_is_not_changed_during_email_change(email_changer, user, order):
    changer = email_changer(order, email=user.email)

    changer()
    user.refresh_from_db()

    assert user.first_name == "Kamaz"
    assert user.last_name == "Otkhodov"


def test_user_is_created_if_email_does_not_exist(email_changer, order):
    changer = email_changer(order, email="circus@gmail.com")

    changer()
    order.refresh_from_db()

    assert order.user.email == "circus@gmail.com"
    assert order.user.first_name == ""
    assert order.user.last_name == ""


def test_order_not_reshipped_when_it_is_not_paid(email_changer, order, ship, unship):
    order.paid = None
    changer = email_changer(order, email="circus@gmail.com")

    changer()

    ship.assert_not_called()
    unship.assert_not_called()


def test_order_is_reshipped_when_it_was_paid(email_changer, factory, course, ship, unship, user):
    order = factory.order(item=course, is_paid=True)
    changer = email_changer(order=order, email=user.email)

    changer()

    ship.assert_called_with(order.course, to=user, order=order), "should be reshipped to the new user"
    unship.assert_called_once_with(order=order)


def test_first_and_last_name_remain_the_same_after_email_change(email_changer, factory, user, course):
    order = factory.order(user=user, item=course)
    changer = email_changer(order, email="circus@gmail.com")

    changer()

    assert order.user.email == "circus@gmail.com"
    assert order.user.first_name == "Kamaz"
    assert order.user.last_name == "Otkhodov"
