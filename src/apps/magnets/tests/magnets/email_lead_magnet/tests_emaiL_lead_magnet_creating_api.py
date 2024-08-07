import pytest

from apps.users.models import User

pytestmark = [pytest.mark.django_db]


def get_user():
    return User.objects.last()


@pytest.fixture
def lead_data():
    return {
        "name": "Monty Python",
        "email": "monty@python.org",
        "recaptcha": "__TESTING__",
    }


def test_creating(api, lead_data):
    api.post("/api/v2/leads/email/eggs/", lead_data, format="multipart")

    created = get_user()

    assert created.first_name == "Monty"
    assert created.last_name == "Python"
    assert created.email == "monty@python.org"


def test_creating_response(api, lead_data):
    got = api.post("/api/v2/leads/email/eggs/", lead_data, format="multipart")

    assert got["ok"] is True
    assert got["message"] == "No spam, only ham"


def test_nameless(api, lead_data):
    del lead_data["name"]

    api.post("/api/v2/leads/email/eggs/", lead_data, format="multipart")

    created = get_user()

    assert created.email == "monty@python.org"


def test_emailless_should_fail(api, lead_data):
    del lead_data["email"]

    api.post("/api/v2/leads/email/eggs/", lead_data, format="multipart", expected_status_code=400)


def test_recaptcha_fail(api, lead_data, settings):
    settings.DRF_RECAPTCHA_TESTING_PASS = False

    got = api.post("/api/v2/leads/email/eggs/", lead_data, format="multipart", expected_status_code=400)

    assert "Error" in got["recaptcha"][0]
