import pytest

from apps.a12n.utils import decode_jwt_without_validation

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def random_user(mixer):
    return mixer.blend("users.User")


def test(api, mixer, random_user):
    superuser = mixer.blend("users.User", is_superuser=True)
    api.auth(superuser)

    got = api.get(f"/api/v2/auth/as/{random_user.pk}/")
    token = decode_jwt_without_validation(got["token"])

    assert token["user_id"] == random_user.id


def test_no_anon(anon, random_user):
    anon.get(f"/api/v2/auth/as/{random_user.pk}/", expected_status_code=401)


def test_no_regular_users(api, mixer, random_user):
    regular_user = mixer.blend("users.User", is_superuser=False)
    api.auth(regular_user)

    api.get(f"/api/v2/auth/as/{random_user.pk}/", expected_status_code=403)
