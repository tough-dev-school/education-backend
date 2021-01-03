import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship_course(mocker):
    return mocker.patch('products.models.Course.ship')


@pytest.fixture
def ship_record(mocker):
    return mocker.patch('products.models.Record.ship')


@pytest.fixture
def another_record(mixer):
    return mixer.blend('courses.Record')


def test_shipping_course(bundle, user, course, ship_course):
    bundle.courses.add(course)

    bundle.ship(to=user)

    ship_course.assert_called_once()


def test_shipping_record(bundle, user, record, ship_record):
    bundle.records.add(record)

    bundle.ship(to=user)

    ship_record.assert_called_once()


def test_shipping_empty(bundle, user, ship_record, ship_course):
    bundle.ship(to=user)

    ship_course.assert_not_called()
    ship_record.assert_not_called()


def test_shipping_multiple_records(bundle, user, record, another_record, ship_record):
    bundle.records.add(record, another_record)

    bundle.ship(to=user)

    assert ship_record.call_count == 2
