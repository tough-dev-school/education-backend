import pytest

pytestmark = [pytest.mark.django_db]


def test_list(api, course):
    got = api.get('/api/v2/studies/purchased/')['results']

    assert got[0]['id'] == course.id
    assert got[0]['slug'] == 'ichteology'
    assert got[0]['name'] == 'Ихтеология для 5 класса'


@pytest.mark.usefixtures('unpaid_order')
def test_list_includes_only_purchased(api):
    got = api.get('/api/v2/studies/purchased/')['results']

    assert len(got) == 0


def test_list_excludes_courses_that_should_not_be_displayed_in_lms(api, course):
    course.setattr_and_save('display_in_lms', False)

    got = api.get('/api/v2/studies/purchased/')['results']

    assert len(got) == 0


def test_no_anon(anon):
    anon.get('/api/v2/studies/purchased/', expected_status_code=401)
