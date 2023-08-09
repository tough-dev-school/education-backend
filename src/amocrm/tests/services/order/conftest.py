import pytest


@pytest.fixture(autouse=True)
def _mock_tasks_with_paid_setter(mocker):
    mocker.patch("orders.services.order_paid_setter.OrderPaidSetter.update_user_tags", return_value=None)


@pytest.fixture
def order(factory, amocrm_course, amocrm_user):
    factory.amocrm_user_contact(user=amocrm_user.user)
    order = factory.order(course=amocrm_course.course, user=amocrm_user.user)
    order.set_paid()
    return order
