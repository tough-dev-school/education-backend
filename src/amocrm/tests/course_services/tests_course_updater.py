import pytest

from amocrm.services.course_updater import AmoCRMCourseUpdater
from amocrm.types import AmoCRMElement

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.course_updater.get_product_field_id", return_value=333)
    mocker.patch("amocrm.services.course_updater.get_catalog_id", return_value=777)


@pytest.fixture
def amocrm_course(factory, course):
    return factory.amocrm_course(course=course, amocrm_id=999)


@pytest.fixture
def updated_element(element_fields):
    return AmoCRMElement(id=999, name="TopCourse", custom_fields_values=element_fields)


@pytest.fixture
def mock_update_catalog_element(mocker, updated_element):
    return mocker.patch("amocrm.client.AmoCRMClient.update_catalog_element", return_value=updated_element)


@pytest.fixture
def course_updater():
    return lambda amocrm_course: AmoCRMCourseUpdater(amocrm_course)()


def test_updates_correct_call(course_updater, amocrm_course, mock_update_catalog_element, updated_element):
    course_updater(amocrm_course)

    mock_update_catalog_element.assert_called_once_with(
        catalog_id=777,
        element=updated_element,
    )


@pytest.mark.usefixtures("mock_update_catalog_element")
def test_update_amocrm_course(course_updater, amocrm_course):
    got = course_updater(amocrm_course)

    assert got == amocrm_course.amocrm_id
