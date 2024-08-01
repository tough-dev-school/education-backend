import pytest


@pytest.fixture
def order(factory, amocrm_course, amocrm_user):
    order = factory.order(item=amocrm_course.course, user=amocrm_user.user, is_paid=True)
    return order


@pytest.fixture
def amocrm_lead(mixer, order):
    return mixer.blend("amocrm.AmoCRMOrderLead", order=order, amocrm_id=481516)


@pytest.fixture
def paid_order_with_lead(user, course, factory, amocrm_lead):
    order = factory.order(user=user, item=course, is_paid=True, author=user, amocrm_lead=amocrm_lead)
    return order


@pytest.fixture
def paid_order_without_lead(user, course, factory):
    return factory.order(user=user, item=course, is_paid=True, author=user)


@pytest.fixture(autouse=True)
def set_current_user(_set_current_user):
    return _set_current_user
