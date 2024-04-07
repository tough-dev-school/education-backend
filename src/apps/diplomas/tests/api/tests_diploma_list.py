import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("diploma"),
]


def test_no_anon(anon):
    anon.get("/api/v2/diplomas/", expected_status_code=401)


def test_ok(api, diploma):
    api.auth(diploma.study.student)

    got = api.get("/api/v2/diplomas/")["results"]

    assert len(got[0]) == 6
    assert diploma.slug in got[0]["url"]
    assert got[0]["slug"] == diploma.slug
    assert got[0]["student"]["uuid"] == str(diploma.study.student.uuid)
    assert got[0]["course"]["name"] == diploma.study.course.name
    assert got[0]["language"] == diploma.language
    assert ".gif" in got[0]["image"]


def test_no_diplomas_of_other_users(api):
    got = api.get("/api/v2/diplomas/")["results"]

    assert len(got) == 0


def test_superuser_can_access_diplomas_of_other_users(api):
    api.user.update(is_superuser=True)

    got = api.get("/api/v2/diplomas/")["results"]

    assert len(got) == 1


def test_user_with_permission_can_access_diplomas_of_other_users(api):
    api.user.add_perm("diplomas.diploma.access_all_diplomas")

    got = api.get("/api/v2/diplomas/")["results"]

    assert len(got) == 1


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "True",
        "true",
        "1",
    ],
)
def test_pagination_could_be_disable_with_query_param(api, diploma, disable_pagination_value):
    api.auth(diploma.study.student)

    got = api.get(f"/api/v2/diplomas/?disable_pagination={disable_pagination_value}")

    assert len(got) == 1
    assert got[0]["slug"] == diploma.slug


@pytest.mark.parametrize(
    "disable_pagination_value",
    [
        "false",
        "False",
        "any-other-value",
    ],
)
def test_paginated_response_with_disable_pagination_false_or_invalid_value(api, diploma, disable_pagination_value):
    api.auth(diploma.study.student)

    got = api.get(f"/api/v2/diplomas/?disable_pagination={disable_pagination_value}")

    assert "results" in got
    assert "count" in got
    assert len(got["results"]) == 1
