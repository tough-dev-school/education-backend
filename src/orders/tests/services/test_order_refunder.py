import pytest
from ipaddress import IPv4Address

from banking.selector import BANK_CHOICES
from banking.selector import BANKS
from orders.models import Refund
from orders.services import OrderRefunder

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.DANGEROUS_OPERATION_HAPPENED_EMAILS = [
        "first_refunds_watcher@mail.com",
        "second_refunds_watcher@mail.com",
    ]

    settings.ABSOLUTE_HOST = "http://absolute-url.url"


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Петруша", last_name="Золотов")


@pytest.fixture
def course(factory):
    return factory.course(name="Нитроглицерин в домашних условиях")


@pytest.fixture
def paid_order(factory, course):
    order = factory.order(
        is_paid=True,
        bank_id=BANK_CHOICES[0],
        price=999,
    )
    order.set_item(course)

    return order


@pytest.fixture(autouse=True)
def mock_send_mail(mocker):
    return mocker.patch("mailing.tasks.send_mail.delay")


@pytest.fixture
def refunder(paid_order, user):
    return lambda order=paid_order, author=user: OrderRefunder(
        order=order,
        author=author,
        author_ip=IPv4Address("17.253.144.10"),
    )()


def test_refund_for_order_created(refunder, paid_order, user):
    refunder()

    refund = Refund.objects.last()
    assert refund is not None
    assert refund.order == paid_order
    assert refund.author == user
    assert refund.author_ip == "17.253.144.10"
    assert refund.bank_confirmation_received is False, "Refund should not be confirmed by default"


def test_all_refund_watchers_notified(refunder, mock_send_mail, mocker):
    refunder()

    mock_send_mail.assert_has_calls(
        any_order=True,
        calls=[
            mocker.call(to="first_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
            mocker.call(to="second_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
        ],
    )


def test_refund_notification_email_context_and_template_correct(refunder, paid_order, mock_send_mail, mocker):
    refunder()

    mock_send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        ctx=dict(
            refunded_item="Нитроглицерин в домашних условиях",
            price="999",
            bank=BANKS[BANK_CHOICES[0]].name,
            author="Петруша Золотов",
            author_ip="17.253.144.10",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{paid_order.id}/change/",
        ),
    )
