import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.mark.parametrize('time, should_be_sent', [
    ['2032-11-01 15:30', False],  # earlier
    ['2032-12-01 16:00', False],  # too early
    ['2032-12-02 16:00', False],  # too early
    ['2032-12-03 16:00', False],  # too early
    ['2032-12-04 16:00', True],  # OK
    ['2032-12-05 16:00', True],  # TODO Check this condition
    ['2032-12-06 16:00', True],  # TODO Check this condition
    ['2032-12-07 16:00', False],  # late
])
def test(freezer, trigger, time, should_be_sent):
    freezer.move_to(time)

    assert trigger.should_be_sent() is should_be_sent
