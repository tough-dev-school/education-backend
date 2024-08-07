import pytest

pytestmark = [
    pytest.mark.django_db,
]


def test_items(dolyame):
    got = dolyame.get_items()

    assert len(got) == 1

    assert len(got[0]) == 4
    assert got[0]["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert got[0]["quantity"] == 1
    assert got[0]["price"] == "100500"
    assert got[0]["receipt"]["payment_method"] == "full_payment"
    assert got[0]["receipt"]["tax"] == "none"
    assert got[0]["receipt"]["payment_object"] == "service"
    assert got[0]["receipt"]["measurement_unit"] == "шт"


def test_user(dolyame):
    got = dolyame.get_client_info()

    assert got["first_name"] == "Авраам Соломонович"
    assert got["last_name"] == "Пейзенгольц"
    assert got["email"] == "avraam-the-god@gmail.com"
