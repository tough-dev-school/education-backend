from contextlib import nullcontext as does_not_raise
from datetime import datetime
from datetime import timezone
import pytest

from core import current_user
from apps.banking.selector import BANKS
from apps.orders.services import OrderRefunder
from apps.orders.services import OrderUnshipper
from apps.banking.exceptions import BankDoesNotExist

pytestmark = [
    pytest.mark.django_db,
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
def _set_current_user(user):
    current_user.set_current_user(user)


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
def not_paid_order(factory, user, course):
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
    assert paid_order.unpaid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)
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


def test_do_not_break_if_current_user_could_not_be_captured(refund, paid_order, mock_send_mail, get_send_mail_call_email_context):
    current_user.unset_current_user()

    with does_not_raise():
        refund(paid_order)

    send_mail_context = get_send_mail_call_email_context(mock_send_mail)
    assert send_mail_context["refund_author"] == "unknown"


def test_update_user_tags(paid_order, mock_rebuild_tags, refund):
    paid_order.user.update(email="")

    refund(paid_order)

    mock_rebuild_tags.assert_called_once_with(student_id=paid_order.user.id, subscribe=False)


@pytest.mark.usefixtures("_enable_amocrm")
def test_call_update_user_celery_chain_with_subscription(paid_order, refund, mocker):
    mock_celery_chain = mocker.patch("celery.chain")
    mock_first_rebuild_tags = mocker.patch("apps.users.tasks.rebuild_tags.si")
    mock_second_push_customer = mocker.patch("apps.amocrm.tasks.push_user.si")
    mock_third_return_order_in_amocrm = mocker.patch("apps.amocrm.tasks.return_order.si")

    refund(paid_order)

    mock_celery_chain.assert_called_once_with(
        mock_first_rebuild_tags(student_id=paid_order.user.id, subscribe=True),
        mock_second_push_customer(user_id=paid_order.user.id),
        mock_third_return_order_in_amocrm(order_id=paid_order.id),
    )


def test_fail_if_bank_is_set_but_unknown(paid_order, refund):
    paid_order.update(bank_id="tinkoff_credit")

    with pytest.raises(BankDoesNotExist, match="does not exists"):
        refund(paid_order)
