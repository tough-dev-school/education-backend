import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api):
    got = api.get('/api/v2/users/me/')

    assert got['id'] == api.user.pk
    assert got['uuid'] == str(api.user.uuid)
    assert got['username'] == api.user.username
    assert got['first_name'] == api.user.first_name
    assert got['last_name'] == api.user.last_name
    assert got['first_name_en'] == api.user.first_name_en
    assert got['last_name_en'] == api.user.last_name_en


def test_anon(anon):
    got = anon.get('/api/v2/users/me/', as_response=True)

    assert got.status_code == 401


def test_edit_user_data(api):
    api.patch('/api/v2/users/me/', {
        'first_name': 'Kamaz',
        'last_name': 'Otkhodov',
    })

    api.user.refresh_from_db()

    assert api.user.first_name == 'Kamaz'
    assert api.user.last_name == 'Otkhodov'


def test_edit_user_data_in_english(api):
    api.patch('/api/v2/users/me/', {
        'first_name_en': 'Kamaz',
        'last_name_en': 'OfWaste',
    })

    api.user.refresh_from_db()

    assert api.user.first_name_en == 'Kamaz'
    assert api.user.last_name_en == 'OfWaste'


def test_edit_user_data_response(api):
    got = api.patch('/api/v2/users/me/', {
        'first_name': 'Kamaz',
        'last_name': 'Otkhodov',
    })

    assert got['id'] == api.user.id
    assert got['username'] == api.user.username
    assert got['first_name'] == 'Kamaz'
    assert got['last_name'] == 'Otkhodov'
