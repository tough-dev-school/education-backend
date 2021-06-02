import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture(autouse=True)
def order(factory, course, user):
    order = factory.order(user=user)
    order.set_item(course)
    order.set_paid()

    return order


def test_sending_mail(course, user, send_mail):
    course.send_email_to_all_purchased_users(template_id='100500')

    send_mail.assert_called_once_with(to=user.email, template_id='100500')


def test_non_purchased(course, user, send_mail, order):
    order.set_not_paid()

    course.send_email_to_all_purchased_users(template_id='100500')

    send_mail.assert_not_called()
