import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('diploma'),
]


def test_no_anon(anon):
    anon.get('/api/v2/diplomas/', expected_status_code=401)


def test_ok(api, diploma):
    api.auth(diploma.study.student)

    got = api.get('/api/v2/diplomas/')['results']

    assert got[0]['slug'] == str(diploma.slug)
    assert got[0]['student']['uuid'] == str(diploma.study.student.uuid)
    assert got[0]['course']['name'] == diploma.study.course.name


def test_no_diplomas_of_other_users(api):
    got = api.get('/api/v2/diplomas/')['results']

    assert len(got) == 0


def test_superuser_can_access_diploams_of_other_users(api):
    api.user.is_superuser = True
    api.user.save()

    got = api.get('/api/v2/diplomas/')['results']

    assert len(got) == 1


def test_user_with_permission_can_access_diploms_of_other_users(api):
    api.user.add_perm('diplomas.diploma.access_all_diplomas')

    got = api.get('/api/v2/diplomas/')['results']

    assert len(got) == 1
