from contextlib import nullcontext as does_not_raise
from datetime import datetime
from datetime import timezone as dt_timezone
import pytest

from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.banking.exceptions import BankDoesNotExist
from apps.banking.selector import BANKS
from apps.orders.services import OrderRefunder
from apps.orders.services import OrderUnshipper
from core import current_user

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


@pytest.fixture(autouse=True)
def _adjust_settings(settings):
    settings.BANKS_REFUNDS_ENABLED = True
    settings.ABSOLUTE_HOST = "http://absolute-url.url"

    settings.DANGEROUS_OPERATION_HAPPENED_EMAILS = [
        "first_refunds_watcher@mail.com",
        "second_refunds_watcher@mail.com",
    ]


@pytest.fixture
def _enable_amocrm(settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"


@pytest.fixture(autouse=True)
def mock_dolyame_refund(mocker):
    return mocker.patch("apps.tinkoff.dolyame.Dolyame.refund")


@pytest.fixture(autouse=True)
def mock_send_mail(mocker):
    return mocker.patch("apps.mailing.tasks.send_mail.delay")


@pytest.fixture
def spy_unshipper(mocker):
    return mocker.spy(OrderUnshipper, "__call__")


@pytest.fixture
def get_send_mail_call_email_context():
    return lambda mock_send_mail: mock_send_mail.mock_calls[0].kwargs["ctx"]


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
def refund():
    return lambda order: OrderRefunder(order=order)()


@pytest.mark.freeze_time("2032-12-01 15:30Z")
def test_set_order_unpaid_and_unshipped(paid_order, refund):
    refund(paid_order)

    paid_order.refresh_from_db()
    assert paid_order.paid is None
    assert paid_order.unpaid == datetime(2032, 12, 1, 15, 30, tzinfo=dt_timezone.utc)
    assert paid_order.shipped is None
    assert not hasattr(paid_order, "study"), "Study record should be deleted at this point"


def test_refund_order_in_bank(paid_order, refund, mock_dolyame_refund):
    refund(paid_order)

    mock_dolyame_refund.assert_called_once()


def test_call_unshipper_to_unship(paid_order, refund, spy_unshipper):
    refund(paid_order)

    spy_unshipper.assert_called_once()
    called_service = spy_unshipper.call_args.args[0]
    assert called_service.order == paid_order


def test_do_not_set_unpaid_if_order_unpaid(not_paid_order, refund):
    refund(not_paid_order)

    not_paid_order.refresh_from_db()
    assert not_paid_order.paid is None
    assert not_paid_order.unpaid is None


def test_do_not_call_bank_refund_if_order_unpaid(not_paid_order, refund, mock_dolyame_refund):
    refund(not_paid_order)

    mock_dolyame_refund.assert_not_called()


def test_do_not_call_bank_refund_if_refunds_disabled(paid_order, refund, mock_dolyame_refund, settings):
    settings.BANKS_REFUNDS_ENABLED = False

    refund(paid_order)

    mock_dolyame_refund.assert_not_called()


def test_do_not_break_and_not_try_call_bank_refund_if_bank_id_is_empty(paid_order, refund):
    paid_order.update(bank_id="")

    with does_not_raise():
        refund(paid_order)


def test_unship_order_despite_it_unpaid(not_paid_order, refund, spy_unshipper):
    refund(not_paid_order)

    spy_unshipper.assert_called_once()


def test_order_refunded_all_refund_watchers_notified(paid_order, refund, mock_send_mail, mocker):
    refund(paid_order)

    mock_send_mail.assert_has_calls(
        any_order=True,
        calls=[
            mocker.call(to="first_refunds_watcher@mail.com", template_id=mocker.ANY, disable_antispam=mocker.ANY, ctx=mocker.ANY),
            mocker.call(to="second_refunds_watcher@mail.com", template_id=mocker.ANY, disable_antispam=mocker.ANY, ctx=mocker.ANY),
        ],
    )


def test_refund_notification_email_context_and_template_correct(refund, paid_order, mock_send_mail, mocker):
    refund(paid_order)

    mock_send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        disable_antispam=True,
        ctx=dict(
            order_id=paid_order.id,
            refunded_item="Кройка и шитьё",
            refund_author="Авраам Соломонович Пейзенгольц",
            payment_method_name=BANKS["dolyame"].name,
            price="999",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{paid_order.id}/change/",
        ),
    )


def test_do_not_break_if_order_without_item_was_refunded(refund, paid_order, mock_send_mail, get_send_mail_call_email_context):
    paid_order.update(course=None)

    with does_not_raise():
        refund(paid_order)

    send_mail_context = get_send_mail_call_email_context(mock_send_mail)
    assert send_mail_context["refunded_item"] == "not-set"


def test_break_if_current_user_could_not_be_captured(mocker, refund):
    mocker.patch("apps.orders.services.order_refunder.get_current_user", return_value=None)

    with pytest.raises(AttributeError):
        refund(paid_order)


def test_update_user_tags(paid_order, mock_rebuild_tags, refund):
    paid_order.user.update(email="")

    refund(paid_order)

    mock_rebuild_tags.assert_called_once_with(student_id=paid_order.user.id)


@pytest.mark.dashamail
def test_update_dashamail(paid_order, refund, mocker):
    update_subscription = mocker.patch("apps.dashamail.tasks.DashamailSubscriber.subscribe")

    refund(paid_order)

    update_subscription.assert_called_once()


@pytest.mark.usefixtures("_enable_amocrm")
def test_amocrm_is_updated(paid_order, refund, mocker):
    push_user = mocker.patch("apps.amocrm.tasks.AmoCRMUserPusher.__call__")
    push_order = mocker.patch("apps.amocrm.tasks.AmoCRMOrderPusher.__call__")

    refund(paid_order)

    push_user.assert_called_once()
    push_order.assert_called_once()


def test_fail_if_bank_is_set_but_unknown(paid_order, refund):
    paid_order.update(bank_id="tinkoff_credit")

    with pytest.raises(BankDoesNotExist, match="does not exists"):
        refund(paid_order)


@pytest.mark.auditlog
@pytest.mark.freeze_time
def test_success_admin_log_created(paid_order, refund, user):
    refund(paid_order)

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order refunded"
    assert log.content_type_id == ContentType.objects.get_for_model(paid_order).id
    assert log.object_id == str(paid_order.id)
    assert log.object_repr == str(paid_order)
    assert log.user == user
