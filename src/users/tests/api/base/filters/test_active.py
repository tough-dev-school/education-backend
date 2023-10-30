import pytest

pytestmark = pytest.mark.django_db

url = "/api/v2/users/"


@pytest.fixture
def ya_user(factory):
    return factory.user()


@pytest.mark.parametrize(
    ("is_active", "length"),
    [
        (True, 2),
        (False, 1),
    ],
)
def test_ok(as_superuser, is_active, length, ya_user):
    ya_user.update(is_active=is_active)

    response = as_superuser.get(url)

    assert len(response) == length
