from datetime import datetime
import pytest

from _decimal import Decimal

from django.utils import timezone


@pytest.fixture(autouse=True)
def _mock_cached_fields_id(mocker):
    mocker.patch("amocrm.dto.customer.get_contact_field_id", return_value=2235143)
    mocker.patch("amocrm.dto.lead.get_catalog_id", return_value=777)
    mocker.patch("amocrm.dto.transaction.get_catalog_id", return_value=777)
    mocker.patch("amocrm.dto.lead.get_b2c_pipeline_id", return_value=555)
    mocker.patch("amocrm.dto.lead.get_b2c_pipeline_status_id", return_value=333)


@pytest.fixture
def user(user):
    user.email = "dada@da.net"
    user.first_name = "First"
    user.last_name = "Last"
    user.tags = ["b2b", "any-purchase"]
    user.save()
    return user


@pytest.fixture
def order(amocrm_user, amocrm_course, factory):
    order = factory.order(
        user=amocrm_user.user,
        course=amocrm_course.course,
        price=Decimal(100),
        slug="Gu2g7SXFxfepif4UkLNhzx",
        amocrm_transaction__amocrm_id=22222,
        amocrm_lead__amocrm_id=11111,
    )
    order.created = datetime.fromtimestamp(1672520400, tz=timezone.get_current_timezone())
    order.save()
    return order


@pytest.fixture
def post(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.post")


@pytest.fixture
def patch(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.patch")


@pytest.fixture
def delete(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.delete")
