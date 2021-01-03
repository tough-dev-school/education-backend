import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture(autouse=True)
def order(mixer, course, user):
    return mixer.blend('orders.Order', user=user, course=course, paid=timezone.now())


def test_sending_mail(course, user, send_mail):
    course.send_email_to_all_purchased_users(template_id='100500')

    send_mail.assert_called_once_with(to=user.email, template_id='100500')


def test_non_purchased(course, user, send_mail, order):
    order.setattr_and_save('paid', None)

    course.send_email_to_all_purchased_users(template_id='100500')

    send_mail.assert_not_called()
