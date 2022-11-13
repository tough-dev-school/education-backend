import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30Z'),
]


@pytest.fixture
def another_order(factory, user):
    return factory.order(user=user, paid='2032-12-01 15:20Z')


@pytest.mark.usefixtures('another_order')
def test_not_sending_with_another_order(trigger, freezer):
    freezer.move_to('2032-12-02 16:00')

    assert trigger.should_be_sent() is False


@pytest.mark.parametrize('change_another_order', [
    lambda another_order: another_order.setattr_and_save('created', '2031-01-01 15:30Z'),  # more then a year ago
    lambda another_order: another_order.setattr_and_save('paid', None),
])
def test_sending(another_order, change_another_order, trigger, freezer):
    freezer.move_to('2032-12-02 16:00')

    change_another_order(another_order)

    assert trigger.should_be_sent() is True


def test_sending_when_order_belongs_to_another_user(another_order, trigger, freezer, mixer):
    another_user = mixer.blend('users.User')
    freezer.move_to('2032-12-02 16:00')

    another_order.setattr_and_save('user', another_user)

    assert trigger.should_be_sent() is True
