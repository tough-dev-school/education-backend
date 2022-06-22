import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def api_call(mocker):
    return mocker.patch('tinkoff.credit.TinkoffCredit.call', return_value={'link': '__mocked'})


def test_items(tinkoff):
    got = tinkoff.get_items()

    assert len(got) == 1

    assert got[0]['name'] == 'Предоставление доступа к записи курса «Пентакли и Тентакли»'
    assert got[0]['quantity'] == 1
    assert got[0]['price'] == 100500


def test_user(tinkoff):
    got = tinkoff.get_user()

    assert got['contact']['fio']['firstName'] == 'Авраам Соломонович'
    assert got['contact']['fio']['lastName'] == 'Пейзенгольц'


def test_order_data(tinkoff, order, api_call):
    tinkoff.get_initial_payment_url()

    got = api_call.call_args[1]['payload']

    assert got['shopId'] == '1234'
    assert got['showcaseId'] == '123-45'
    assert got['sum'] == 100500
    assert got['orderNumber'] == order.slug
    assert got['items'][0]['name'] == 'Предоставление доступа к записи курса «Пентакли и Тентакли»'
    assert got['values']['contact']['fio']['firstName'] == 'Авраам Соломонович'


def test_return_value(tinkoff):
    url = tinkoff.get_initial_payment_url()

    assert url == '__mocked'
