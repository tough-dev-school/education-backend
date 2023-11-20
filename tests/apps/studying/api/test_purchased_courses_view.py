import pytest

pytestmark = [pytest.mark.django_db]


def test_list(api, course):
    got = api.get("/api/v2/studies/purchased/")["results"]

    assert got[0]["id"] == course.id
    assert got[0]["slug"] == "ichteology"
    assert got[0]["name"] == "Ихтеология для 5 класса"
    assert got[0]["home_page_slug"] is None
    assert ".gif" in got[0]["cover"]
    assert "http://" in got[0]["cover"]


@pytest.mark.usefixtures("unpaid_order")
def test_list_includes_only_purchased(api):
    got = api.get("/api/v2/studies/purchased/")["results"]

    assert len(got) == 0


def test_list_excludes_courses_that_should_not_be_displayed_in_lms(api, course):
    course.update(display_in_lms=False)

    got = api.get("/api/v2/studies/purchased/")["results"]

    assert len(got) == 0


def test_no_anon(anon):
    anon.get("/api/v2/studies/purchased/", expected_status_code=401)


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, course, disable_pagination_value):
    got = api.get(f"/api/v2/studies/purchased/?disable_pagination={disable_pagination_value}")

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
def test_paginated_response_with_disable_pagination_false_or_invalid_value(api, course, disable_pagination_value):
    got = api.get(f"/api/v2/studies/purchased/?disable_pagination={disable_pagination_value}")

    assert "results" in got
    assert "count" in got
    assert len(got["results"]) == 1
