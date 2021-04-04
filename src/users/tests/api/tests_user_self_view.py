import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api):
    got = api.get('/api/v2/users/me/')

    assert got['id'] == api.user.pk
    assert got['username'] == api.user.username


def test_anon(anon):
    got = anon.get('/api/v2/users/me/', as_response=True)

    assert got.status_code == 401
