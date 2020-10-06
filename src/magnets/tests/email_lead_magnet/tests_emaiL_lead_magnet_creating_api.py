import pytest

from users.models import User

pytestmark = [pytest.mark.django_db]


def get_user():
    return User.objects.last()


def test_creating(api):
    api.post('/api/v2/leads/email/eggs/', {
        'name': 'Monty Python',
        'email': 'monty@python.org',
    }, format='multipart')

    created = get_user()

    assert created.first_name == 'Monty'
    assert created.last_name == 'Python'
    assert created.email == 'monty@python.org'


def test_creating_response(api):
    got = api.post('/api/v2/leads/email/eggs/', {
        'name': 'Monty Python',
        'email': 'monty@python.org',
    }, format='multipart')

    assert got['ok'] is True
    assert got['message'] == 'No spam, only ham'


def test_nameless(api):
    api.post('/api/v2/leads/email/eggs/', {
        'email': 'monty@python.org',
    }, format='multipart')

    created = get_user()

    assert created.email == 'monty@python.org'


def test_wrong_email(api):
    api.post('/api/v2/leads/email/eggs/', {
        'name': 'Monty Python',
    }, format='multipart', expected_status_code=400)
