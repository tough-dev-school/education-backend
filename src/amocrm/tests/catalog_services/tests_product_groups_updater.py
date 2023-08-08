import pytest

from amocrm.models import AmoCRMProductGroup
from amocrm.services.products.product_groups_updater import AmoCRMProductGroupsUpdater
from amocrm.types import AmoCRMCatalogFieldValue

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def group(factory):
    return factory.group(slug="popug")


@pytest.fixture
def another_group(factory):
    return factory.group(slug="hehe")


@pytest.fixture
def amocrm_group(factory, group):
    return factory.amocrm_group(group=group, amocrm_id=6453)


@pytest.fixture
def group_field_values():
    return [
        AmoCRMCatalogFieldValue(id=6453, value="popug"),
        AmoCRMCatalogFieldValue(id=7777, value="hehe"),
    ]


@pytest.fixture(autouse=True)
def mock_get_catalogs(mocker, group_field_values):
    return mocker.patch("amocrm.client.AmoCRMClient.update_catalog_field", return_value=group_field_values)


@pytest.fixture(autouse=True)
def mock_get_catalog_id(mocker):
    return mocker.patch("amocrm.services.products.product_groups_updater.get_catalog_id", return_value=777)


@pytest.fixture(autouse=True)
def mock_get_product_field_id(mocker):
    return mocker.patch("amocrm.services.products.product_groups_updater.get_product_field_id", return_value=333)


@pytest.fixture
def groups_updater():
    return AmoCRMProductGroupsUpdater()


@pytest.mark.usefixtures("group", "another_group")
def test_creates_amocrm_group(groups_updater):
    groups_updater()

    assert AmoCRMProductGroup.objects.count() == 2
    assert AmoCRMProductGroup.objects.get(amocrm_id=6453).group.slug == "popug"
    assert AmoCRMProductGroup.objects.get(amocrm_id=7777).group.slug == "hehe"


@pytest.mark.usefixtures("group", "another_group")
def test_correct_params_client_call(groups_updater, mock_get_catalogs):
    groups_updater()

    mock_get_catalogs.assert_called_once_with(
        catalog_id=777,
        field_id=333,
        field_values=[
            AmoCRMCatalogFieldValue(value="popug"),
            AmoCRMCatalogFieldValue(value="hehe"),
        ],
    )


@pytest.mark.usefixtures("another_group", "amocrm_group")
def test_correct_params_client_call_when_exist(groups_updater, mock_get_catalogs, factory):
    groups_updater()

    mock_get_catalogs.assert_called_once_with(
        catalog_id=777,
        field_id=333,
        field_values=[
            AmoCRMCatalogFieldValue(value="hehe"),
            AmoCRMCatalogFieldValue(id=6453, value="popug"),
        ],
    )
