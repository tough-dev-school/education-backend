import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", username="rulon.oboev@gmail.com", email="rulon.oboev@gmail.com")
