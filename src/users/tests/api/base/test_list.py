import pytest

pytestmark = pytest.mark.django_db


def test_response(as_superuser):
    response = as_superuser.get("/api/v2/users/")[0]

    user = as_superuser.user
    assert response["email"] == user.email
    assert response["first_name"] == user.first_name
    assert response["first_name_en"] == user.first_name_en
    assert response["gender"] == user.gender
    assert response["github_username"] == user.github_username
    assert response["id"] == user.id
    assert response["last_name"] == user.last_name
    assert response["last_name_en"] == user.last_name_en
    assert response["linkedin_username"] == user.linkedin_username
    assert response["name"] == user.__str__()
    assert response["telegram_username"] == user.telegram_username
    assert response["username"] == user.username
    assert response["uuid"] == str(user.uuid)

    assert set(response) == {
        "id",
        "email",
        "first_name",
        "first_name_en",
        "gender",
        "github_username",
        "last_name",
        "last_name_en",
        "linkedin_username",
        "name",
        "telegram_username",
        "username",
        "uuid",
    }


def test_perfomance(as_superuser, django_assert_num_queries, factory):
    factory.cycle(2).user()

    with django_assert_num_queries(2):
        as_superuser.get(f"/api/v2/users/")
