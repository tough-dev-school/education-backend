import pytest
import requests_mock

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mailjet(mailjet):
    with requests_mock.Mocker() as m:
        mailjet.http_mock = m

        yield mailjet


def test_ok(mailjet, user):
    def assertion(req, res):
        query = req.json()

        assert query['Email'] == 'test@e.mail'
        assert query['Properties']['firstname'] == 'Rulon'
        assert query['Properties']['lastname'] == 'Oboev'
        assert query['Properties']['name'] == 'Rulon Oboev'

        res.status_code = 201
        return {'ok': 'mocked'}

    mailjet.http_mock.post('https://api.eu.mailjet.com/v3/REST/contactslist/100500/managecontact', json=assertion)

    mailjet.subscribe(user)


@pytest.mark.xfail(reason='Just to check if above works')
def test_fail(mailjet, user):
    def assertion(req, res):
        query = req.json()

        assert query['Email'] == 'WRONG!1'

        res.status_code = 201
        return {'ok': 'mocked'}

    mailjet.http_mock.post('https://api.eu.mailjet.com/v3/REST/contactslist/100500/managecontact', json=assertion)
    mailjet.subscribe(user)
