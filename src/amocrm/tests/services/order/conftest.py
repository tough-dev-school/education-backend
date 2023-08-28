import pytest


@pytest.fixture
def order(factory, amocrm_course, amocrm_user):
    factory.amocrm_user_contact(user=amocrm_user.user)
    order = factory.order(course=amocrm_course.course, user=amocrm_user.user)
    order.set_paid()
    return order


@pytest.fixture
def amocrm_lead(factory, order):
    return factory.amocrm_order_lead(order=order, amocrm_id=481516)


@pytest.fixture
def paid_order_with_lead(user, course, factory, amocrm_lead):
    return factory.order(user=user, course=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)
