import pytest

pytestmark = [pytest.mark.django_db]


def test_retrieving(api):
    got = api.get(f'/api/v2/users/{api.user.pk}/')

    assert got['username'] == api.user.username


def test_invalid_user(api):
    api.get('/api/v2/users/1000050000/', expected_status_code=404)


def test_anon(anon, api):
    anon.get(f'/api/v2/users/10000050000/', expected_status_code=401)
