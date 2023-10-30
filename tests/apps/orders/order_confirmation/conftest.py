import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(
        price=0,
        confirmation_success_url="https://well.done",
    )


@pytest.fixture
def order(factory, course):
    return factory.order(item=course)


@pytest.fixture(autouse=True)
def ship(mocker):
    return mocker.patch("apps.products.models.Course.ship")
