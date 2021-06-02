import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def record(mixer):
    return mixer.blend('products.Record')


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle')


@pytest.fixture
def order(factory, bundle):
    order = factory.order(item=bundle)
    order.save()

    return order


@pytest.fixture
def bundle(mixer, course, record):
    bundle = mixer.blend('products.Bundle')
    bundle.courses.add(course)
    bundle.records.add(record)

    return bundle


@pytest.fixture
def unship_course(mocker):
    return mocker.patch('products.models.Course.unship')


@pytest.fixture
def unship_record(mocker):
    return mocker.patch('products.models.Record.unship')


def test_bundle_unshipment(bundle, order, unship_record, unship_course):
    """Big integration test that tests Bundle.unship(), Course.unship() and Record.unship() at the same time"""
    bundle.unship(order)

    unship_record.assert_called_once()
    unship_course.assert_called_once()
