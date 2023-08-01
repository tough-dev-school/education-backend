import pytest

from amocrm.models import AmoCRMCourse
from amocrm.services.course_creator import AmoCRMCourseCreator
from amocrm.services.course_creator import AmoCRMCourseCreatorException
from amocrm.types import AmoCRMCatalog
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from amocrm.types import AmoCRMCatalogField

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch(
        "amocrm.services.product_catalog_fields_manager.AmoCRMProductCatalogFieldsManager.get_product_field",
        return_value=AmoCRMCatalogField(id=333, name="aa", type="bb", code="EVERYTHING"),
    )
    mocker.patch(
        "amocrm.services.products_catalog_getter.AmoCRMSProductsCatalogGetter.__call__", return_value=AmoCRMCatalog(id=777, name="products", type="products")
    )


@pytest.fixture
def course(factory):
    group = factory.group(slug="top-group")
    return factory.course(name="TopCourse", slug="top-course", price=99, group=group)


@pytest.fixture
def element_fields():
    price_value = AmoCRMCatalogElementFieldValue(value=99)
    sku_value = AmoCRMCatalogElementFieldValue(value="top-course")
    group_value = AmoCRMCatalogElementFieldValue(value="top-group")
    return [
        AmoCRMCatalogElementField(field_id=333, values=[price_value]),
        AmoCRMCatalogElementField(field_id=333, values=[sku_value]),
        AmoCRMCatalogElementField(field_id=333, values=[group_value]),
    ]


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
    course_creator(course)

    amocrm_course = AmoCRMCourse.objects.get()
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
