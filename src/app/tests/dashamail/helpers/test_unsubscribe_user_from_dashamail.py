import pytest

from app.integrations.dashamail.helpers import unsubscribe_user_from_dashamail

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def unsubscribe_from_dashamail(mocker):
    return mocker.patch('app.tasks.dashamail.unsubscribe_from_dashamail.delay')


def test(user, unsubscribe_from_dashamail):
    unsubscribe_user_from_dashamail(user=user)

    unsubscribe_from_dashamail.assert_called_once_with(email=user.email)
