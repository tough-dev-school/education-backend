import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def amocrm_lead(mixer):
    return mixer.blend("amocrm.AmoCRMOrderLead", amocrm_id=1781381)


@pytest.fixture
def order_with_lead(order, amocrm_lead):
    order.update(amocrm_lead=amocrm_lead)
    return order
