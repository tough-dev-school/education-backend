import pytest

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def fail_response_json():
    return {
        'response': {
            'msg': {
                'err_code': 4,
                'text': 'error',
                'type': 'message',
            },
            'data': {},
        },
    }


def test_subscribe(dashamail, post, dashamail_member):
    dashamail.update_subscription(
        list_id='test-list-id',
        member=dashamail_member,
    )

    post.assert_called_once_with(
        url='',
        payload={
            'email': 'test@e.mail',
            'list_id': 'test-list-id',
            'merge_1': 'Rulon',
            'merge_2': 'Oboev',
            'merge_3': 'test-tag;tag-test',
            'method': 'lists.add_member',
            'update': True,
        },
    )


def test_subscription_failed(dashamail, dashamail_member, fail_response_json):
    dashamail.http_mock.post('https://api.dashamail.com', json=fail_response_json)

    with pytest.raises(DashamailSubscriptionFailed):
        dashamail.update_subscription(
            list_id='',
            member=dashamail_member,
        )
