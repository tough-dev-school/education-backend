import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course()


@pytest.fixture
def another_course(factory):
    return factory.course()


@pytest.fixture(autouse=True)
def lesson(factory, course):
    return factory.lesson(course=course)


@pytest.fixture
def another_lesson(factory, course):
    return factory.lesson(course=course)


@pytest.fixture(autouse=True)
def purchase(factory, api, course):
    return factory.order(user=api.user, item=course, is_paid=True)


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()


def test_ok(api, course, lesson):
    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert len(got["results"]) == 1
    assert got["results"][0]["name"] == lesson.name
    assert got["results"][0]["id"] == lesson.id


@pytest.mark.usefixtures("_no_purchase")
def test_zero_lessons_if_no_purchase(api, course):
    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert len(got["results"]) == 0


def test_401_for_anon_users(anon, course):
    anon.get(f"/api/v2/lessons/?course={course.slug}", expected_status_code=401)


def test_no_results_for_non_existent_course(api):
    got = api.get("/api/v2/lessons/?course=non-existent")

    assert len(got["results"]) == 0


def test_filter_works(api, another_course):
    got = api.get(f"/api/v2/lessons/?course={another_course.slug}")

    assert len(got["results"]) == 0


def test_hidden_lessons_not_shown(api, course, lesson):
    lesson.update(hidden=True)

    got = api.get(f"/api/v2/lessons/?course={course.slug}")

    assert len(got["results"]) == 0
