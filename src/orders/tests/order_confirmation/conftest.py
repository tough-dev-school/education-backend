import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend(
        "products.Course",
        price=0,
        confirmation_success_url="https://well.done",
    )


@pytest.fixture
def order(factory, course):
    return factory.order(item=course)


@pytest.fixture(autouse=True)
def ship(mocker):
    return mocker.patch("products.models.Course.ship")
