import pytest

from app.integrations.mailchimp import MailchimpMember

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(('email', 'hash'), [
    ('test@gmail.com', '1aedb8d9dc4751e229a335e371db8058'),
    ('TEST@gmAIl.CoM', '1aedb8d9dc4751e229a335e371db8058'),
])
def test(email, hash):
    member = MailchimpMember(
        email=email,
        first_name='',
        last_name='',
    )

    assert member.subscriber_hash == hash
