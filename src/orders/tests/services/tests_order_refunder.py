from datetime import datetime
from datetime import timezone
import pytest

from banking.selector import BANKS
from orders.services import OrderRefunder

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
def mock_dolyame_refund(mocker):
    return mocker.patch("tinkoff.dolyame.Dolyame.refund")


@pytest.fixture(autouse=True)
def mock_send_mail(mocker):
    return mocker.patch("mailing.tasks.send_mail.delay")


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.delay")


@pytest.fixture
def order(factory, user, course):
    order = factory.order(
        user=user,
        item=course,
        price=999,
        bank_id="dolyame",  # any bank should be suitable here
    )

    order.ship()
    order.setattr_and_save("paid", datetime.fromisoformat("2022-12-10 09:23Z"))  # set manually to skip side effects
    return order


@pytest.fixture
def refund(order):
    return lambda order=order: OrderRefunder(order=order)()


@pytest.mark.freeze_time("2032-12-01 15:30Z")
def test_set_order_unpaid(order, refund):
    refund()

    order.refresh_from_db()
    assert order.paid is None
    assert order.shipped is None
    assert order.unpaid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)


def test_remove_study_record(order, refund):
    refund()

    order.refresh_from_db()
    assert not hasattr(order, "study"), "Study record should be deleted at this point"


def test_call_item_unshipping(order, refund, mock_item_unshipping):
    refund()

    mock_item_unshipping.assert_called_once_with(order=order)


def test_update_user_tags(order, mock_rebuild_tags, refund):
    order.user.email = ""
    order.user.save()

    refund()

    mock_rebuild_tags.assert_called_once_with(student_id=order.user.id, subscribe=False)


@pytest.mark.usefixtures("_enable_amocrm")
def test_call_update_user_celery_chain_with_subscription(order, refund, mocker):
    mock_celery_chain = mocker.patch("celery.chain")
    mock_first_rebuild_tags = mocker.patch("users.tasks.rebuild_tags.si")
    mock_second_push_customer = mocker.patch("amocrm.tasks.push_user.si")
    mock_third_return_order_in_amocrm = mocker.patch("amocrm.tasks.return_order.si")

    refund()

    mock_celery_chain.assert_called_once_with(
        mock_first_rebuild_tags(student_id=order.user.id, subscribe=True),
        mock_second_push_customer(user_id=order.user.id),
        mock_third_return_order_in_amocrm(order_id=order.id),
    )


def test_empty_item_does_not_break_things(order, refund, mock_item_unshipping):
    order.setattr_and_save("course", None)

    refund(order=order)

    mock_item_unshipping.assert_not_called()


def test_all_refund_watchers_notified(refund, mock_send_mail, mocker):
    refund()

    mock_send_mail.assert_has_calls(
        any_order=True,
        calls=[
            mocker.call(to="first_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
            mocker.call(to="second_refunds_watcher@mail.com", template_id=mocker.ANY, ctx=mocker.ANY),
        ],
    )


def test_refund_notification_email_context_and_template_correct(refund, order, mock_send_mail, mocker):
    refund()

    mock_send_mail.assert_called_with(
        to=mocker.ANY,
        template_id="order-refunded",
        ctx=dict(
            refunded_item="Кройка и шитьё",
            price="999",
            bank_name=BANKS["dolyame"].name,
            author="unknown",
            order_admin_site_url=f"http://absolute-url.url/admin/orders/order/{order.id}/change/",
        ),
    )
