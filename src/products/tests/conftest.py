import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def testcode(mixer):
    return mixer.blend('orders.PromoCode', name='TESTCODE', discount_percent=10)


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch('app.tasks.subscribe_to_mailchimp.delay')


@pytest.fixture
def default_user_data():
    """Data used during purchase tests. Shortcut just to save typing time"""
    return {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }
