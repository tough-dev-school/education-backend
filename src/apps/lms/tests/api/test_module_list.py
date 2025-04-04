import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api, course, lesson):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 1
    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["name"] == lesson.name


@pytest.mark.usefixtures("_no_purchase")
def test_zero_modules_if_no_purchase(api, course):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 0


def test_401_for_anon_users(anon, course):
    anon.get(f"/api/v2/lms/modules/?course={course.pk}", expected_status_code=401)


def test_no_results_for_non_existent_course(api):
    api.get("/api/v2/lms/modules/?course=10005000", expected_status_code=400)


def test_filter_works(api, another_course):
    got = api.get(f"/api/v2/lms/modules/?course={another_course.pk}")

    assert len(got["results"]) == 0


def test_hidden_modules_not_shown(api, course, module):
    module.update(hidden=True)

    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 0


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, course, lesson, disable_pagination_value):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}&disable_pagination={disable_pagination_value}")

    assert got[0]["id"] == lesson.id
