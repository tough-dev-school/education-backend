import pytest

from shipping.shipments import CourseShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend(
        'courses.Course',
        name='Кройка и шитьё',
        name_genitive='Кройки и шитья',
    )


@pytest.fixture
def shipment(user, course):
    return CourseShipment(user, course)


@pytest.fixture(autouse=True)
def invite_to_clickmeeting(mocker):
    return mocker.patch('app.tasks.invite_to_clickmeeting.delay')


@pytest.fixture(autouse=True)
def invite_to_zoomus(mocker):
    return mocker.patch('app.tasks.invite_to_zoomus.delay')
