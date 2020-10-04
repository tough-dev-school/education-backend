import pytest

from users.models import User

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def campaign(mixer):
    return mixer.blend('magnets.EmailLeadMagnetCampaign', slug='eggs')


def get_user():
    return User.objects.last()


def test_creating(api):
    api.post('/api/v2/leads/email/eggs/', {
        'name': 'Monty Python',
        'email': 'monty@python.org',
    })

    created = get_user()

    assert created.first_name == 'Monty'
    assert created.last_name == 'Python'
    assert created.email == 'monty@python.org'


def test_wrong_name(api):
    api.post('/api/v2/leads/email/eggs/', {
        'email': 'monty@python.org',
    }, expected_status_code=400)


def test_wrong_email(api):
    api.post('/api/v2/leads/email/eggs/', {
        'name': 'Monty Python',
    }, expected_status_code=400)
