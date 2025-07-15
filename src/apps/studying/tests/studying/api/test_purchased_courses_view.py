import pytest

pytestmark = [pytest.mark.django_db]


def test_fields(api, course):
    got = api.get("/api/v2/purchased-courses/")["results"]

    assert got[0]["id"] == course.id
    assert got[0]["slug"] == "ichteology"
    assert got[0]["name"] == "Ихтеология для 5 класса"
    assert got[0]["home_page_slug"] is None

    assert ".gif" in got[0]["cover"]
    assert "http://" in got[0]["cover"]

    assert got[0]["chat"] == "https://t.me/chat"
    assert got[0]["calendar_ios"] == "ios://cal"
    assert got[0]["calendar_google"] == "google://cal"

    assert got[0]["links"] == []


def test_links(api, course, mixer):
    mixer.blend("lms.CourseLink", course=course, name="Как учиться", url="/materials/e0e245e30a5a439b91402ba46144b51c")
    mixer.blend("lms.CourseLink", course=course, name="Как учиться 2", url="https://how.to.learn.com")

    got = api.get("/api/v2/purchased-courses/")["results"]

    assert got[0]["links"][0]["name"] == "Как учиться"
    assert got[0]["links"][0]["url"] == "/materials/e0e245e30a5a439b91402ba46144b51c"
    assert got[0]["links"][1]["name"] == "Как учиться 2"
    assert got[0]["links"][1]["url"] == "https://how.to.learn.com"


@pytest.mark.usefixtures("unpaid_order")
def test_list_includes_only_purchased(api):
    got = api.get("/api/v2/purchased-courses/")["results"]

    assert len(got) == 0


@pytest.mark.usefixtures("unpaid_order")
def test_list_includes_all_courses_if_user_has_permission(api):
    api.user.add_perm("studying.study.purchased_all_courses")
    got = api.get("/api/v2/purchased-courses/")["results"]

    assert len(got) == 1


@pytest.mark.usefixtures("unpaid_order")
def test_list_includes_all_courses_if_user_is_a_superuser(api):
    api.user.update(is_superuser=True)
    got = api.get("/api/v2/purchased-courses/")["results"]

    assert len(got) == 1


def test_list_excludes_courses_that_should_not_be_displayed_in_lms(api, course):
    course.update(display_in_lms=False)

    got = api.get("/api/v2/purchased-courses/")["results"]

    assert len(got) == 0


def test_no_anon(anon):
    anon.get("/api/v2/purchased-courses/", expected_status_code=401)


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, course, disable_pagination_value):
    got = api.get(f"/api/v2/purchased-courses/?disable_pagination={disable_pagination_value}")

    assert len(got) == 1
    assert got[0]["id"] == course.id


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "false",
        "False",
        "any-other-value",
    ],
)
def test_paginated_response_with_disable_pagination_false_or_invalid_value(api, disable_pagination_value):
    got = api.get(f"/api/v2/purchased-courses/?disable_pagination={disable_pagination_value}")

    assert "results" in got
    assert "count" in got
    assert len(got["results"]) == 1
