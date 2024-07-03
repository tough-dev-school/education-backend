from _decimal import Decimal
from datetime import datetime

import pytest
from django.utils import timezone


@pytest.fixture(autouse=True)
def _mock_cached_fields_id(mocker):
    mocker.patch("apps.amocrm.ids.contact_field_id", return_value=2235143)
    mocker.patch("apps.amocrm.ids.product_field_id", return_value=800)
    mocker.patch("apps.amocrm.ids.products_catalog_id", return_value=900)
    mocker.patch("apps.amocrm.ids.b2c_pipeline_id", return_value=555)
    mocker.patch("apps.amocrm.ids.b2c_pipeline_status_id", return_value=333)


@pytest.fixture
def user(user):
    return user.update(
        email="dada@da.net",
        first_name="First",
        last_name="Last",
        tags=["b2b", "any-purchase"],
    )


@pytest.fixture
def course(amocrm_course, factory):
    return factory.course(
        name="Popug",
        slug="popug-003",
        price=200,
        group=factory.group(slug="popug-group"),
        amocrm_course=amocrm_course,
    )


@pytest.fixture
def order(amocrm_user, course, factory):
    order = factory.order(
        user=amocrm_user.user,
        item=course,
        price=Decimal(100),
        slug="Gu2g7SXFxfepif4UkLNhzx",
        amocrm_transaction__amocrm_id=22222,
        amocrm_lead__amocrm_id=11111,
    )

    return order.update(created=datetime.fromtimestamp(1672520400, tz=timezone.get_current_timezone()))


@pytest.fixture
def post(mocker):
    return mocker.patch("apps.amocrm.client.http.post")


@pytest.fixture
def patch(mocker):
    return mocker.patch("apps.amocrm.client.http.patch")


@pytest.fixture
def delete(mocker):
    return mocker.patch("apps.amocrm.client.http.delete")


@pytest.fixture
def get(mocker):
    return mocker.patch("apps.amocrm.client.http.get")
