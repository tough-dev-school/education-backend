import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record')


@pytest.mark.parametrize('template_id, expected', [
    [None, None],
    ['', None],
    ['100500', '100500'],
])
def test(record, template_id, expected):
    record.template_id = template_id

    assert record.get_template_id() == expected
