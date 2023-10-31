import pytest

from apps.amocrm.dto import AmoCRMLead

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_create_lead_response(post):
    post.return_value = [
        {
            "id": 11111,
            "contact_id": 5555,
            "company_id": None,
            "request_id": ["0"],
            "merged": False,
        },
    ]


@pytest.fixture
def mock_create_lead(mocker):
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLead._create_lead", return_value=11111)


@pytest.fixture
def mock_link_course_to_lead(mocker):
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLead._link_course_to_lead")


@pytest.fixture
def mock_update_price(mocker):
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLead._set_price_from_order")


@pytest.mark.usefixtures("mock_create_lead", "mock_link_course_to_lead", "mock_update_price")
def test_create_return_lead_id(order):
    lead_id = AmoCRMLead(order=order).create()

    assert lead_id == 11111


def test_create(order, mock_create_lead, mock_link_course_to_lead, mock_update_price):
    AmoCRMLead(order=order).create()

    mock_create_lead.assert_called_once()
    mock_link_course_to_lead.assert_called_once_with(lead_id=11111, course_id=999111)
    mock_update_price.assert_called_once_with(lead_id=11111)


@pytest.mark.usefixtures("_successful_create_lead_response")
def test_create_lead_response(order, post):
    got = AmoCRMLead(order=order)._create_lead()

    assert got == 11111


def test_create_lead(order, post):
    AmoCRMLead(order=order)._create_lead()

    post.assert_called_once_with(
        url="/api/v4/leads/complex",
        data=[
            {
                "status_id": 333,
                "pipeline_id": 555,
                "price": 100,
                "created_at": 1672520400,
                "_embedded": {"contacts": [{"id": 5555}]},
            },
        ],
    )


def test_update_lead_status(order, patch):
    AmoCRMLead(order=order).update(status="closed")

    patch.assert_called_once_with(
        url="/api/v4/leads",
        data=[
            {
                "id": 11111,
                "status_id": 333,
                "pipeline_id": 555,
                "price": 100,
                "created_at": 1672520400,
            },
        ],
    )


def test_update_lead(order, patch):
    AmoCRMLead(order=order).update()

    patch.assert_called_once_with(
        url="/api/v4/leads",
        data=[
            {
                "id": 11111,
                "pipeline_id": 555,
                "price": 100,
                "created_at": 1672520400,
            },
        ],
    )


def test_link_course_to_lead(order, post):
    AmoCRMLead(order=order)._link_course_to_lead(lead_id=5555, course_id=8888)

    post.assert_called_once_with(
        url="/api/v4/leads/5555/link",
        data=[
            {
                "to_entity_id": 8888,
                "to_entity_type": "catalog_elements",
                "metadata": {
                    "quantity": 1,
                    "catalog_id": 900,
                },
            },
        ],
    )
