import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def set_current_user(_set_current_user):
    return _set_current_user


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture
def course(factory):
    return factory.course(name="Ихтеология для 5 класса", slug="ichteology")


@pytest.fixture(autouse=True)
def order(factory, course, api):
    return factory.order(
        user=api.user,
        item=course,
        is_paid=True,
    )


@pytest.fixture
def unpaid_order(order):
    order.refund(order.price)

    return order
