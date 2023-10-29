import pytest

from rest_framework import status

pytestmark = pytest.mark.django_db


@pytest.fixture
def study(course, factory):
    return factory.study(course=course)


def test_response_with_study_course_ok(as_superuser, study):
    response = as_superuser.get(f"/api/v2/users/?course={study.course.id}")[0]

    student = study.student
    assert response["id"] == student.id
    assert response["name"] == student.__str__()

    assert set(response) == {"id", "name"}


@pytest.mark.usefixtures("user")
def test_response_with_course_without_students_ok(as_superuser, course):
    response = as_superuser.get(f"/api/v2/users/?course={course.id}")

    assert not response


@pytest.mark.usefixtures("course")
def test_request_without_course_query_param_raises_not_found(as_superuser):
    as_superuser.get("/api/v2/users/", expected_status_code=status.HTTP_404_NOT_FOUND)


def test_response_students_ordered_by_first_name_asc(as_superuser, course, factory):
    factory.cycle(3).study(course=course)

    response = as_superuser.get(f"/api/v2/users/?course={course.id}")

    assert response[0]["name"] < response[1]["name"] < response[2]["name"]


def test_response_students_ordered_by_last_name_asc(as_superuser, course, factory):
    for student in factory.cycle(3).user(first_name="одинаковое-у-всех"):
        factory.study(course=course, student=student)

    response = as_superuser.get(f"/api/v2/users/?course={course.id}")

    assert response[0]["name"] < response[1]["name"] < response[2]["name"]


def test_perfomance(as_superuser, course, django_assert_num_queries, factory):
    factory.cycle(3).study(course=course)

    with django_assert_num_queries(3):
        as_superuser.get(f"/api/v2/users/?course={course.id}")
