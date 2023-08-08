import pytest

from amocrm.models import AmoCRMCourse
from amocrm.services.products.course_creator import AmoCRMCourseCreator
from amocrm.services.products.course_creator import AmoCRMCourseCreatorException
from amocrm.types import AmoCRMCatalogElement

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.products.course_creator.get_product_field_id", return_value=333)
    mocker.patch("amocrm.services.products.course_creator.get_catalog_id", return_value=777)


@pytest.fixture
def created_element(element_fields):
    return AmoCRMCatalogElement(id=999, name="TopCourse", custom_fields_values=element_fields)


@pytest.fixture(autouse=True)
def mock_create_catalog_element(mocker, created_element):
    return mocker.patch("amocrm.client.AmoCRMClient.create_catalog_element", return_value=created_element)


@pytest.fixture
def course_creator():
    return lambda course: AmoCRMCourseCreator(course)()


def test_creates_amocrm_course(course_creator, course):
    got = course_creator(course)

    amocrm_course = AmoCRMCourse.objects.get()
    assert got == amocrm_course.amocrm_id
    assert amocrm_course.course == course
    assert amocrm_course.amocrm_id == 999


def test_creates_correct_call(course_creator, course, mock_create_catalog_element, element_fields):
    course_creator(course)

    mock_create_catalog_element.assert_called_once_with(
        catalog_id=777,
        element=AmoCRMCatalogElement(name="TopCourse", custom_fields_values=element_fields),
    )


def test_fails_if_already_exist(course_creator, course, factory):
    factory.amocrm_course(course=course)

    with pytest.raises(AmoCRMCourseCreatorException):
        course_creator(course)
