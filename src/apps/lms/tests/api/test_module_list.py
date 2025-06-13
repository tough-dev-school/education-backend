import pytest

pytestmark = [pytest.mark.django_db]


def test_fields(api, course, module):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 1
    assert got["results"][0]["id"] == module.id
    assert got["results"][0]["name"] == "Первая неделя"
    assert got["results"][0]["description"] == "Самая важная неделя"
    assert got["results"][0]["start_date"] == "2032-12-01T15:30:00+03:00"


def test_empty_start_date(api, course, module):
    module.update(start_date=None)

    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert got["results"][0]["start_date"] is None


def test_markdown_in_text(api, course, module):
    module.update(text="*should be rendered*")

    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert "<em>should be rendered</em>" in got["results"][0]["text"]


@pytest.mark.usefixtures("_no_purchase")
def test_zero_modules_if_no_purchase(api, course):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 0


@pytest.mark.usefixtures("_no_purchase")
def test_all_modules_for_users_with_permissions(api, course):
    api.user.add_perm("studying.study.purchased_all_courses")

    got = api.get(f"/api/v2/lms/modules/?course={course.pk}")

    assert len(got["results"]) == 1


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
def test_pagination_could_be_disable_with_query_param(api, course, module, disable_pagination_value):
    got = api.get(f"/api/v2/lms/modules/?course={course.pk}&disable_pagination={disable_pagination_value}")

    assert got[0]["id"] == module.id


def test_query_count(api, module, course, factory, django_assert_num_queries):
    module.delete()

    for _ in range(15):
        factory.module(
            course=course,
        )

    with django_assert_num_queries(7):
        got = api.get(f"/api/v2/lms/modules/?course={course.pk}")
        assert len(got["results"]) == 15
