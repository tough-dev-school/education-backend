import pytest

from apps.users.services import UserCreator

pytestmark = [pytest.mark.django_db]


def test_existing_user(user):
    created = UserCreator(name="Камаз Отходов", email="rulon.oboev@gmail.com")()

    created.refresh_from_db()

    assert created == user


def test_two_users_with_same_email(user, mixer):
    mixer.blend("users.User", email="rulon.oboev@gmail.com")
    created = UserCreator(name="Камаз Отходов", email="rulon.oboev@gmail.com")()

    created.refresh_from_db()

    assert created == user


def test_two_users_with_same_email_case_is_case_insensitive(user, mixer):
    mixer.blend("users.User", username="RULON.OBOEV@gmail.com", email="11@gmail.com")
    created = UserCreator(name="Камаз Отходов", email="rulon.oboev@gmail.com")()

    created.refresh_from_db()

    assert created == user


def test_existing_user_name_does_not_change(user):
    created = UserCreator(name="Камаз Отходов", email="rulon.oboev@gmail.com")()

    created.refresh_from_db()

    assert created.first_name == user.first_name
    assert created.last_name == user.last_name
    assert created.first_name != "Камаз"
    assert created.last_name != "Отходов"


def test_user_with_another_email_case_is_the_same(user):
    created = UserCreator(name="Камаз Отходов", email="RuLoN.oBoEV@gmAil.cOm")()
    assert created == user


def test_user_creates_if_existing_inactive(user):
    user.update(
        is_active=False,
        username=user.uuid,  # should differ from email to be able to create new account
    )

    created = UserCreator(name="Камаз Отходов", email=user.email)()

    assert created != user
