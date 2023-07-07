import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("template_id", "expected"),
    [
        (None, None),
        ("", None),
        ("100500", "100500"),
    ],
)
def test(course, template_id, expected):
    course.template_id = template_id

    assert course.get_template_id() == expected
