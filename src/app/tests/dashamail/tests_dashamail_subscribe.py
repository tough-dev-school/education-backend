import pytest

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed

pytestmark = [pytest.mark.django_db]


def test_subscribe(dashamail, post, user):
    dashamail.subscribe_user(
        list_id='test-list-id',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    post.assert_called_once_with(
        url='',
        payload={
            'email': 'test@e.mail',
            'list_id': 'test-list-id',
            'merge_1': 'Rulon',
            'merge_2': 'Oboev',
            'method': 'lists.add_member',
            'update': True,
        },
    )


def test_subscribe_with_tags(dashamail, post, user):
    dashamail.subscribe_user(
        list_id='test-list-id',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=['test', 'TEST'],
    )

    post.assert_called_once_with(
        url='',
        payload={
            'email': 'test@e.mail',
            'list_id': 'test-list-id',
            'merge_1': 'Rulon',
            'merge_2': 'Oboev',
            'merge_3': 'test;TEST',
            'method': 'lists.add_member',
            'update': True,
        },
    )


def test_subscription_failed(dashamail, user, fail_response_json):
    dashamail.httpx_mock.add_response(url='https://api.dashamail.com', method='POST', json=fail_response_json)

    with pytest.raises(DashamailSubscriptionFailed):
        dashamail.subscribe_user(
            list_id='test-list-id',
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        )
