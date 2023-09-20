from contextlib import nullcontext as does_not_raise
from ipaddress import IPv4Address
import pytest

from banking.selector import BANKS
from orders.models import Refund
from orders.services import OrderRefunder
from orders.services.order_refunder import OrderRefunderException
from orders.services.order_unpaid_setter import OrderUnpaidSetter

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
def not_paid_order(factory):
    return factory.order(is_paid=False)


@pytest.fixture
def paid_order(factory, course):
    order = factory.order(
        bank_id="dolyame",  # any bank should suite here, but we prefer to choose not default one
        price=999,
    )

    order.set_item(course)
    order.set_paid()

    return order


@pytest.fixture(autouse=True)
def mock_send_mail(mocker):
    return mocker.patch("mailing.tasks.send_mail.delay")


@pytest.fixture
def refund(paid_order, user):
    return lambda order=paid_order, author=user: OrderRefunder(
        order=order,
        author=author,
        author_ip=IPv4Address("17.253.144.10"),
    )()  # noqa: JS101


def test_refund_entry_for_order_created(refund, paid_order, user):
    refund()

    refund = Refund.objects.last()
    assert refund is not None
    assert refund.order == paid_order
    assert refund.author == user
    assert refund.author_ip == "17.253.144.10"
    assert refund.bank_confirmation_received is False, "Refund should not be confirmed by default"


def test_order_unshipped_and_marked_unpaid(refund, mocker, paid_order):
    spy_unpaid_setter = mocker.spy(OrderUnpaidSetter, "__call__")

    refund()

    paid_order.refresh_from_db()
    assert paid_order.paid is None
    assert paid_order.shipped is None
    spy_unpaid_setter.assert_called_once()


def test_all_refund_watchers_notified(refund, mock_send_mail, mocker):
    refund()

    mock_send_mail.assert_has_calls(
        any_order=True,
        calls=[
            mocker.call(to="first_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
            mocker.call(to="second_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
        ],
    )


def test_refund_notification_email_context_and_template_correct(refund, paid_order, mock_send_mail, mocker):
    refund()

    mock_send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        ctx=dict(
            refunded_item="Нитроглицерин в домашних условиях",
            price="999",
            bank=BANKS["dolyame"].name,
            author="Петруша Золотов",
            author_ip="17.253.144.10",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{paid_order.id}/change/",
        ),
    )


def test_raise_if_refunds_throttle_limit_exceeded(refund, user, mixer):
    mixer.cycle(5).blend("orders.Refund", author=user)

    with pytest.raises(OrderRefunderException, match="To many"):
        refund()


@pytest.mark.freeze_time("2023-01-01 10:00Z")
def test_do_not_raise_if_time_limit_pass(refund, user, mixer, freezer):
    mixer.cycle(5).blend("orders.Refund", author=user)

    freezer.move_to("2023-01-02 10:01Z")  # 24 hours + 1 second passed

    with does_not_raise():
        refund()


def test_do_not_raise_it_refunds_exists_but_from_other_author(refund, user, another_user, mixer):
    mixer.cycle(5).blend("orders.Refund", author=user)

    with does_not_raise():
        refund(author=another_user)


def test_raise_if_order_is_not_paid(refund, not_paid_order):
    with pytest.raises(OrderRefunderException, match="not paid"):
        refund(order=not_paid_order)


def test_raise_if_order_is_free(refund, paid_order):
    paid_order.setattr_and_save("price", 0)

    with pytest.raises(OrderRefunderException, match="order if free, no refund possible"):
        refund()


def test_order_could_be_paid_and_refunded_twice(refund, paid_order):
    refund(order=paid_order)
    paid_order.set_paid()

    with does_not_raise():
        refund(order=paid_order)
