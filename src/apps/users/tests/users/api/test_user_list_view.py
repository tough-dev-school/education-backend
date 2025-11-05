import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def another_user(mixer):
    return mixer.blend("users.User", email="another@user.com")


@pytest.fixture
def api(api):
    """Set current user to admin"""
    api.user.update(is_staff=True)

    return api


def test(api, another_user):
    got = api.get("/api/v2/users/")["results"]

    assert {str(another_user.uuid), str(api.user.uuid)} == {user["uuid"] for user in got}
    assert {another_user.email, api.user.email} == {user["email"] for user in got}


def test_admin_only(api):
    api.user.update(is_staff=False)

    api.get("/api/v2/users/", expected_status_code=403)


def test_no_anon(anon):
    anon.get("/api/v2/users/", expected_status_code=401)


@pytest.mark.parametrize("query", ["no@email.com", "1nv4l1d"])
def test_search_by_email_not_found(api, query):
    got = api.get(f"/api/v2/users/?email={query}")["results"]

    assert len(got) == 0


@pytest.mark.parametrize("query", ["another@user.com", "ANOtHer@USER.com"])
def test_search_by_email_found(api, query):
    got = api.get(f"/api/v2/users/?email={query}")["results"]

    assert len(got) == 1
