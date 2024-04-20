import time
from contextlib import nullcontext as does_not_raise
from datetime import datetime

import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.banking.exceptions import BankDoesNotExist
from apps.banking.selector import BANKS
from apps.orders.models import Refund
from apps.orders.services import OrderRefunder, OrderUnshipper
from apps.orders.services.order_refunder import OrderRefunderException

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user", "send_mail"),
]


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.BANKS_REFUNDS_ENABLED = True
    settings.ABSOLUTE_HOST = "http://absolute-url.url"

    settings.DANGEROUS_OPERATION_HAPPENED_EMAILS = [
        "first_refunds_watcher@mail.com",
        "second_refunds_watcher@mail.com",
    ]


@pytest.fixture(autouse=True)
def mock_dolyame_refund(mocker):
    return mocker.patch("apps.tinkoff.dolyame.Dolyame.refund")


@pytest.fixture(autouse=True)
def mock_tinkoff_refund(mocker):
    return mocker.patch("apps.tinkoff.bank.TinkoffBank.refund")


@pytest.fixture(autouse=True)
def mock_stripe_refund(mocker):
    return mocker.patch("apps.stripebank.bank.StripeBank.refund")


@pytest.fixture
def spy_unshipper(mocker):
    return mocker.spy(OrderUnshipper, "__call__")


@pytest.fixture
def spy_bank_refund(mocker):
    return mocker.spy(OrderRefunder, "do_bank_refund")


@pytest.fixture
def get_send_mail_call_email_context():
    return lambda send_mail: send_mail.mock_calls[0].kwargs["ctx"]


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.delay")


@pytest.fixture
def not_paid_order(course, factory, user):
    order = factory.order(
        user=user,
        item=course,
        price=999,
        bank_id="dolyame",  # any bank should be suitable here
    )

    order.ship()
    return order


@pytest.fixture
def paid_order(not_paid_order):
    return not_paid_order.update(paid=datetime.fromisoformat("2022-12-10 09:23Z"))  # set manually to skip side effects


@pytest.fixture
def paid_tinkoff_order(paid_order):
    return paid_order.update(bank_id="tinkoff_bank")


@pytest.fixture
def paid_stripe_order(paid_order):
    return paid_order.update(bank_id="stripe")


@pytest.fixture
def refund():
    def _refund(order, amount):
        return OrderRefunder(order=order, amount=amount)()

    return _refund


def test_5_per_day_limit(factory, paid_tinkoff_order, refund):
    factory.cycle(5).refund(order=paid_tinkoff_order, amount=100)
    time.sleep(10)

    with pytest.raises(OrderRefunderException) as e:
        refund(paid_tinkoff_order, 100)

    assert "Up to 5 refunds per day are allowed" in str(e)


def test_1_per_10_seconds_limit(paid_tinkoff_order, refund):
    refund(paid_tinkoff_order, 100)

    with pytest.raises(OrderRefunderException) as e:
        refund(paid_tinkoff_order, 100)

    assert "Up to 1 refund per 10 seconds is allowed" in str(e)


def test_refund_shipped_unpaid_order_for_non_zero_amount(not_paid_order, refund):
    with pytest.raises(OrderRefunderException) as e:
        refund(not_paid_order, 100)

    not_paid_order.refresh_from_db()
    assert "Only 0 can be refunded for not paid order" in str(e)
    assert not_paid_order.shipped is not None


def test_refund_shipped_unpaid_order(not_paid_order, refund):
    refund(not_paid_order, 0)

    not_paid_order.refresh_from_db()
    assert not_paid_order.shipped is None


def test_refund_negative_amount(paid_tinkoff_order, refund):
    with pytest.raises(OrderRefunderException) as e:
        refund(paid_tinkoff_order, -1)

    assert "Amount to refund should be more or equal 0" in str(e)


@pytest.mark.freeze_time("2032-12-01 15:30Z")
def test_set_order_unpaid_and_unshipped(paid_order, refund):
    refund(paid_order, paid_order.price)

    paid_order.refresh_from_db()
    assert paid_order.paid is not None
    assert paid_order.shipped is None
    assert not hasattr(paid_order, "study"), "Study record should be deleted at this point"


def test_refund_order_in_bank(paid_order, refund, mock_dolyame_refund):
    refund(paid_order, paid_order.price)

    mock_dolyame_refund.assert_called_once()


def test_call_unshipper_to_unship(paid_order, refund, spy_unshipper):
    refund(paid_order, paid_order.price)

    spy_unshipper.assert_called_once()
    called_service = spy_unshipper.call_args.args[0]
    assert called_service.order == paid_order


def test_do_not_call_bank_refund_if_order_unpaid(not_paid_order, refund, mock_dolyame_refund):
    refund(not_paid_order, 0)

    mock_dolyame_refund.assert_not_called()


def test_do_not_call_bank_refund_if_refunds_disabled(paid_order, refund, mock_dolyame_refund, settings):
    settings.BANKS_REFUNDS_ENABLED = False

    refund(paid_order, paid_order.price)

    mock_dolyame_refund.assert_not_called()


def test_do_not_break_and_not_try_call_bank_refund_if_bank_id_is_empty(paid_order, refund):
    paid_order.update(bank_id="")

    with does_not_raise():
        refund(paid_order, paid_order.price)


def test_unship_order_despite_it_unpaid(not_paid_order, refund, spy_unshipper):
    refund(not_paid_order, 0)

    spy_unshipper.assert_called_once()


def test_order_refunded_all_refund_watchers_notified(paid_order, refund, send_mail, mocker):
    refund(paid_order, paid_order.price)

    send_mail.assert_has_calls(
        any_order=True,
        calls=[
            mocker.call(to="first_refunds_watcher@mail.com", template_id=mocker.ANY, disable_antispam=mocker.ANY, ctx=mocker.ANY),
            mocker.call(to="second_refunds_watcher@mail.com", template_id=mocker.ANY, disable_antispam=mocker.ANY, ctx=mocker.ANY),
        ],
    )


def test_refund_notification_email_context_and_template_correct(refund, paid_order, send_mail, mocker):
    refund(paid_order, paid_order.price)

    send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        disable_antispam=True,
        ctx=dict(
            order_id=paid_order.id,
            refunded_item="Кройка и шитьё",
            refund_author="Авраам Соломонович Пейзенгольц",
            payment_method_name=BANKS["dolyame"].name,
            price="0",
            amount="999",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{paid_order.id}/change/",
        ),
    )


def test_do_not_break_if_order_without_item_was_refunded(refund, paid_order, send_mail, get_send_mail_call_email_context):
    paid_order.update(course=None)

    with does_not_raise():
        refund(paid_order, paid_order.price)

    send_mail_context = get_send_mail_call_email_context(send_mail)
    assert send_mail_context["refunded_item"] == "not-set"


def test_break_if_current_user_could_not_be_captured(mocker, refund):
    mocker.patch("apps.orders.services.order_refunder.get_current_user", return_value=None)

    with pytest.raises(AttributeError):
        refund(paid_order, paid_order.price)


def test_update_user_tags(paid_order, mock_rebuild_tags, refund):
    paid_order.user.update(email="")

    refund(paid_order, paid_order.price)

    mock_rebuild_tags.assert_called_once_with(student_id=paid_order.user.id)


@pytest.mark.dashamail()
def test_update_dashamail(paid_order, refund, mocker):
    update_subscription = mocker.patch("apps.dashamail.tasks.DashamailSubscriber.subscribe")

    refund(paid_order, paid_order.price)

    update_subscription.assert_called_once()


def test_fail_if_bank_is_set_but_unknown(paid_order, refund):
    paid_order.update(bank_id="tinkoff_credit")

    with pytest.raises(BankDoesNotExist, match="does not exists"):
        refund(paid_order, paid_order.price)


@pytest.mark.auditlog()
@pytest.mark.freeze_time()
def test_success_admin_log_created(paid_order, refund, user):
    refund(paid_order, paid_order.price)

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order refunded: refunded amount - 999"
    assert log.content_type_id == ContentType.objects.get_for_model(paid_order).id
    assert log.object_id == str(paid_order.id)
    assert log.object_repr == str(paid_order)
    assert log.user == user


def test_partial_refund_exceed_available_amount(paid_tinkoff_order, refund):
    with pytest.raises(OrderRefunderException) as e:
        refund(paid_tinkoff_order, 1000)

    assert "Amount to refund is more than available" in str(e)


def test_partial_refund_dolyame(paid_order, refund):
    """No partial refunds available for dolyame"""
    with pytest.raises(OrderRefunderException) as e:
        refund(paid_order, 500)

    assert "Partial refund is not available" in str(e)


def test_partial_refund_tinkoff(paid_tinkoff_order, refund):
    paid_tinkoff_order.update(bank_id="tinkoff_bank")

    refund(paid_tinkoff_order, 500)

    paid_tinkoff_order.refresh_from_db()
    assert paid_tinkoff_order.price == 499


def test_partial_refund_stripe(paid_stripe_order, refund):
    paid_stripe_order.update(bank_id="stripe")

    refund(paid_stripe_order, 500)

    paid_stripe_order.refresh_from_db()
    assert paid_stripe_order.price == 499


def test_partial_refund_order_not_unshipped(paid_tinkoff_order, refund, spy_unshipper):
    refund(paid_tinkoff_order, 500)

    spy_unshipper.assert_not_called()


def test_partial_refund_order_unshipped_when_total_refund_eq_price(paid_tinkoff_order, refund, spy_unshipper):
    refund(paid_tinkoff_order, 500)
    time.sleep(10)

    refund(paid_tinkoff_order, 499)

    spy_unshipper.assert_called_once()


@pytest.mark.auditlog()
@pytest.mark.freeze_time()
def test_partial_refund_success_admin_log_created(paid_tinkoff_order, refund, user):
    refund(paid_tinkoff_order, 500)

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order refunded: refunded amount - 500"
    assert log.content_type_id == ContentType.objects.get_for_model(paid_tinkoff_order).id
    assert log.object_id == str(paid_tinkoff_order.id)
    assert log.object_repr == str(paid_tinkoff_order)
    assert log.user == user


def test_partial_refund_notification_email_context_and_template_correct(refund, paid_tinkoff_order, send_mail, mocker):
    refund(paid_tinkoff_order, 500)

    send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        disable_antispam=True,
        ctx=dict(
            order_id=paid_tinkoff_order.id,
            refunded_item="Кройка и шитьё",
            refund_author="Авраам Соломонович Пейзенгольц",
            payment_method_name=BANKS["tinkoff_bank"].name,
            price="499",
            amount="500",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{paid_tinkoff_order.id}/change/",
        ),
    )


def test_partial_refund_not_set_unpaid(paid_tinkoff_order, refund):
    refund(paid_tinkoff_order, 500)

    paid_tinkoff_order.refresh_from_db()
    assert paid_tinkoff_order.price == 499
    assert paid_tinkoff_order.paid is not None


def test_partial_refund_set_unpaid(paid_tinkoff_order, refund):
    refund(paid_tinkoff_order, 999)

    paid_tinkoff_order.refresh_from_db()
    assert paid_tinkoff_order.price == 0
    assert paid_tinkoff_order.paid is not None


def test_refund_is_created(paid_order, refund, user):
    refund(paid_order, paid_order.price)

    refund = Refund.objects.first()
    assert refund.amount == 999
    assert refund.order == paid_order
    assert refund.author == user
    assert refund.bank_id == paid_order.bank_id


def test_partial_refund_is_created(paid_tinkoff_order, refund, user):
    refund(paid_tinkoff_order, 500)

    refund = Refund.objects.first()
    assert refund.amount == 500
    assert refund.order == paid_tinkoff_order
    assert refund.author == user
    assert refund.bank_id == paid_tinkoff_order.bank_id


def test_bank_refund_is_not_called_if_amount_is_zero(paid_tinkoff_order, refund, spy_bank_refund):
    refund(paid_tinkoff_order, 0)

    spy_bank_refund.assert_not_called()
