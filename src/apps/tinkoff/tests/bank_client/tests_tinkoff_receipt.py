import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(order):
    return order.user


def test_tinkoff_receipt(user, tinkoff):
    got = tinkoff.get_receipt()

    assert got["Email"] == user.email
    assert got["Taxation"] == "usn_income"


def test_tinkoff_items(tinkoff):
    got = tinkoff.get_receipt()["Items"]

    assert len(got) == 1

    assert got[0]["Name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert got[0]["Amount"] == 10050000
    assert got[0]["Price"] == 10050000

    assert got[0]["Tax"] == "none"
    assert got[0]["PaymentObject"] == "service"
