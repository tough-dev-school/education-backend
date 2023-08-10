import pytest


@pytest.fixture(autouse=True)
def _mock_tasks_with_paid_setter(mocker):
    mocker.patch("orders.services.order_paid_setter.OrderPaidSetter.after_shipment", return_value=None)
    mocker.patch("orders.services.order_unpaid_setter.OrderUnpaidSetter.after_unshipment", return_value=None)


@pytest.fixture
def order(factory, amocrm_course, amocrm_user):
    factory.amocrm_user_contact(user=amocrm_user.user)
    order = factory.order(course=amocrm_course.course, user=amocrm_user.user)
    order.set_paid()
    return order


@pytest.fixture
def amocrm_lead(factory, order):
    return factory.amocrm_order_lead(order=order, amocrm_id=481516)
