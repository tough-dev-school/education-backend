import pytest

from app.integrations.dashamail.exceptions import DashamailUnsubscriptionFailed

pytestmark = [pytest.mark.django_db]


def test_unsubscription_failed(dashamail, user, fail_response_json):
    dashamail.httpx_mock.add_response(url='https://api.dashamail.com', method='POST', json=fail_response_json)

    with pytest.raises(DashamailUnsubscriptionFailed):
        dashamail.unsubscribe_user(email=user.email)
