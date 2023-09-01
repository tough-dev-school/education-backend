from datetime import datetime
import pytest

from _decimal import Decimal

from django.utils import timezone


@pytest.fixture(autouse=True)
def _mock_cached_fields_id(mocker):
    mocker.patch("amocrm.dto.customer.get_contact_field_id", return_value=2235143)
    mocker.patch("amocrm.dto.product.get_product_field_id", return_value=800)
    mocker.patch("amocrm.dto.product.get_catalog_id", return_value=900)
    mocker.patch("amocrm.dto.group.get_product_field_id", return_value=800)
    mocker.patch("amocrm.dto.group.get_catalog_id", return_value=900)


@pytest.fixture
def user(user):
    user.email = "dada@da.net"
    user.first_name = "First"
    user.last_name = "Last"
    user.tags = ["b2b", "any-purchase"]
    user.save()
    return user


@pytest.fixture
def course(amocrm_course, factory):
    group = factory.group(slug="popug-group")
    amocrm_course.course.name = "Popug"
    amocrm_course.course.slug = "popug-003"
    amocrm_course.course.price = 200
    amocrm_course.course.group = group
    amocrm_course.course.save()
    return amocrm_course.course


@pytest.fixture
def post(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.post")


@pytest.fixture
def patch(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.patch")


@pytest.fixture
def delete(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.delete")
