import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 16:20:40'),
]


def test_items(atol):
    got = atol.get_items()

    assert len(got) == 1

    assert got[0]['name'] == 'Предоставление доступа к записи курса «Пентакли и Тентакли»'
    assert got[0]['quantity'] == 1
    assert got[0]['price'] == 100500
    assert got[0]['sum'] == 100500
    assert got[0]['vat']['type'] == 'none'

    assert 'payment_method' in got[0]
    assert 'payment_object' in got[0]


@pytest.mark.xfail(reason='Atol API can not handle round numbers')
@pytest.mark.parametrize(('price', 'expected'), [
    ('100', '100.00'),
    ('100.10', '100.10'),
    ('100.22', '100.22'),
])
def test_item_price(atol, price, expected):
    atol.order.setattr_and_save('price', price)

    got = atol.get_items()

    assert got[0]['price'] == expected


def test_order_data(atol, post, order):
    atol()

    result = post.call_args[1]['payload']

    assert result['external_id'] == f'tds-{order.id}'
    assert result['timestamp'] == '01.12.2032 16:20:40'


def test_client_data(atol, post):
    atol()

    result = post.call_args[1]['payload']

    assert result['receipt']['client'] == {'email': 'abraham@gmail.com'}


def test_company_data(atol, post):
    atol()

    result = post.call_args[1]['payload']

    assert result['receipt']['company'] == {
        'email': 'receipts@tough-dev.school',
        'inn': '71100500',
        'payment_address': 'Планета Алдераан, Звезда Смерти, док 2204',
    }


def test_receipt_data(atol, post):
    atol()

    result = post.call_args[1]['payload']

    assert result['receipt']['total'] == 100500
    assert result['receipt']['payments'] == [  # NOQA: JS101
        {
            'type': 1,
            'sum': 100500,
        },
    ]
