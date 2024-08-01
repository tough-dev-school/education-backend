import pytest

from apps.amocrm.models import AmoCRMCourse
from apps.amocrm.services.course_pusher import AmoCRMCoursePusher

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_create(mocker):
    return mocker.patch("apps.amocrm.dto.product.AmoCRMProductDTO.create", return_value=555)


@pytest.fixture
def mock_update(mocker):
    return mocker.patch("apps.amocrm.dto.product.AmoCRMProductDTO.update")


def test_call_create_if_amocrm_course_not_exist(course, mock_create):
    AmoCRMCoursePusher(course=course)()

    mock_create.assert_called_once()


@pytest.mark.usefixtures("mock_create")
def test_save_amocrm_course_if_not_exist(course):
    AmoCRMCoursePusher(course=course)()

    amocrm_course = AmoCRMCourse.objects.get()
    assert amocrm_course.amocrm_id == 555
    assert amocrm_course.course == course


@pytest.mark.usefixtures("amocrm_course")
def test_update_amocrm_course_if_exist(course, mock_update):
    AmoCRMCoursePusher(course=course)()

    mock_update.assert_called_once()
