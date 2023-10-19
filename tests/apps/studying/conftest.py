import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.is_superuser = False
    api.user.save()

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
    order.set_not_paid()

    return order
