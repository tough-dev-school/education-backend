import pytest

from users.models import User

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
    assert got['gender'] == api.user.gender
    assert got['linkedin_username'] == api.user.linkedin_username
    assert got['github_username'] == api.user.github_username
    assert got['telegram_username'] == api.user.telegram_username


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
        'first_name_en': 'Bigtruck',
        'last_name_en': 'OfWaste',
    })

    api.user.refresh_from_db()

    assert api.user.first_name_en == 'Bigtruck'
    assert api.user.last_name_en == 'OfWaste'


def test_edit_gender(api):
    api.user.gender = User.GENDERS.MALE
    api.user.save()

    api.patch('/api/v2/users/me/', {'gender': 'female'})

    api.user.refresh_from_db()
    assert api.user.gender == User.GENDERS.FEMALE


@pytest.mark.parametrize('field', ['github_username', 'linkedin_username', 'telegram_username'])
def test_edit_additional_fields(api, field):
    setattr(api.user, field, 'h4x0r')
    api.user.save()

    api.patch('/api/v2/users/me/', {field: 'zeroc00l'})

    api.user.refresh_from_db()
    assert getattr(api.user, field) == 'zeroc00l'


def test_edit_user_data_response(api):
    got = api.patch('/api/v2/users/me/', {
        'first_name': 'Kamaz',
        'last_name': 'Otkhodov',
    })

    assert got['id'] == api.user.id
    assert got['username'] == api.user.username
    assert got['gender'] == api.user.gender
    assert got['first_name'] == 'Kamaz'
    assert got['last_name'] == 'Otkhodov'


def test_user_update_triggers_diploma_regeneration(api, mocker):
    diploma_regenerator = mocker.patch('diplomas.tasks.regenerate_diplomas.delay')

    api.patch('/api/v2/users/me/', {
        'first_name': 'Kamaz',
        'last_name': 'Otkhodov',
    })

    diploma_regenerator.assert_called_once()


@pytest.mark.parametrize('field', ['github_username', 'linkedin_username', 'telegram_username'])
def test_raise_error_is_social_username_used_already(api, field, user):
    setattr(user, field, 'h4x0r')  # set field value user to other user
    user.save()

    got = api.patch('/api/v2/users/me/', {field: 'h4x0r'}, expected_status_code=400)

    assert 'serviceError' in got


@pytest.mark.parametrize('field', ['github_username', 'linkedin_username', 'telegram_username'])
def test_do_not_raise_if_update_his_own_socials(api, field):
    setattr(api.user, field, 'h4x0r')
    api.user.save()

    api.patch('/api/v2/users/me/', {field: 'h4x0r'})  # user update his own socials with same values


@pytest.mark.parametrize('field', ['github_username', 'linkedin_username', 'telegram_username'])
def test_do_not_raise_if_user_clears_socials(api, field, user):
    api.patch('/api/v2/users/me/', {field: ''})  # user update his own socials with same values
