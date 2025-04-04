import pytest

pytestmark = [pytest.mark.django_db]


def test_ok(api, module, lesson):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert len(got["results"]) == 1
    assert got["results"][0]["id"] == lesson.id
    assert got["results"][0]["name"] == lesson.name


@pytest.mark.usefixtures("_no_purchase")
def test_zero_lessons_if_no_purchase(api, module):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert len(got["results"]) == 0


def test_401_for_anon_users(anon, module):
    anon.get(f"/api/v2/lms/lessons/?module={module.pk}", expected_status_code=401)


def test_no_results_for_non_existent_course(api):
    api.get("/api/v2/lms/lessons/?module=10005000", expected_status_code=400)


def test_filter_works(api, another_module):
    got = api.get(f"/api/v2/lms/lessons/?module={another_module.pk}")

    assert len(got["results"]) == 0


def test_hidden_lessons_not_shown(api, module, lesson):
    lesson.update(hidden=True)

    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}")

    assert len(got["results"]) == 0


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, module, lesson, disable_pagination_value):
    got = api.get(f"/api/v2/lms/lessons/?module={module.pk}&disable_pagination={disable_pagination_value}")

    assert got[0]["id"] == lesson.id
