import pytest

from apps.products.models import Course

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-04 15:30:55"),
]


@pytest.fixture
def course(factory):
    course = factory.course()

    course.group.update(created="2032-12-01 15:30:55+03:00", evergreen=False)

    return course


def queryset():
    return Course.objects.for_admin()


def test_on_by_default(course):
    assert course in queryset()


def test_off_after_2_years(course):
    course.group.update(created="2030-12-01 15:30:55+03:00")

    assert course not in queryset()


def test_on_after_2_years_if_evergreen(course):
    course.group.update(
        created="2030-12-01 15:30:55+03:00",
        evergreen=True,
    )
