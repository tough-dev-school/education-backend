import pytest

pytestmark = [pytest.mark.django_db]


def test(mailchimp, mailchimp_member, post):
    mailchimp.set_tags(
        list_id='100500',
        members=[mailchimp_member],
        tags=['aatag', 'bbtag'],
    )

    post.assert_called_once_with(
        url='/lists/100500/members/bac8eb22f0ed07fa57fa5000117fc3de/tags',
        payload={
            'tags': [
                {'name': 'aatag', 'status': 'active'},
                {'name': 'bbtag', 'status': 'active'},
            ],
        },
        expected_status_code=204,
    )
