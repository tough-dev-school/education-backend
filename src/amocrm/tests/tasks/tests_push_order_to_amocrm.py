import pytest

from _decimal import Decimal

from amocrm import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_push_lead(mocker):
    return mocker.patch("amocrm.tasks._push_lead.si")


@pytest.fixture
def mock_push_transaction(mocker):
    return mocker.patch("amocrm.tasks._push_transaction.si")


@pytest.fixture
def mock_link_course_to_lead(mocker):
    return mocker.patch("amocrm.tasks._link_course_to_lead.si")


@pytest.fixture
def mock_chain(mocker):
    return mocker.patch("amocrm.tasks.chain")


@pytest.fixture
def order_with_lead(factory, user, course):
    order = factory.order(id=299, price=100, user=user, course=course, author=user, is_paid=False)
    factory.amocrm_order_lead(order=order)
    return order


@pytest.fixture
def order_without_lead(factory, user, course):
    return factory.order(id=99, price=100, user=user, course=course, author=user, is_paid=False)


@pytest.fixture
def paid_order(factory, user, course):
    return factory.order(id=199, price=100, user=user, course=course, author=user, is_paid=True)


def test_call_with_lead(order_with_lead, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    got = tasks.push_order_to_amocrm(order_id=order_with_lead.id)

    assert got is None
    mock_chain.assert_called_once_with(
        mock_link_course_to_lead(order_id=299),
        mock_push_lead(order_id=299),
        mock_push_transaction(order_id=299),
    )


def test_call_without_lead(order_without_lead, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    got = tasks.push_order_to_amocrm(order_id=order_without_lead.id)

    assert got is None
    mock_chain.assert_called_once_with(
        mock_push_lead(order_id=99),
        mock_link_course_to_lead(order_id=99),
        mock_push_lead(order_id=99),
        mock_push_transaction(order_id=99),
    )


def test_call_paid(paid_order, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain):
    got = tasks.push_order_to_amocrm(order_id=paid_order.id)

    assert got is None
    mock_chain.assert_called_once_with(
        mock_push_lead(order_id=199),
        mock_link_course_to_lead(order_id=199),
        mock_push_lead(order_id=199),
        mock_push_transaction(order_id=199),
    )


def test_get_linked_to_old_duplicate_orders_lead(
    order_without_lead, order_with_lead, mock_push_lead, mock_push_transaction, mock_link_course_to_lead, mock_chain
):
    got = tasks.push_order_to_amocrm(order_id=order_without_lead.id)

    order_without_lead.refresh_from_db()
    assert order_without_lead.amocrm_lead == order_with_lead.amocrm_lead
    mock_chain.assert_called_once_with(
        mock_link_course_to_lead(order_id=99),
        mock_push_lead(order_id=99),
        mock_push_transaction(order_id=99),
    )
    assert got is None


def test_not_push_if_author_not_equal_to_user(order_without_lead, mock_chain, another_user):
    order_without_lead.author = another_user
    order_without_lead.save()

    got = tasks.push_order_to_amocrm(order_id=order_without_lead.id)

    assert got == "not for amocrm"
    mock_chain.assert_not_called()


def test_not_push_if_free_order(order_without_lead, mock_chain):
    order_without_lead.price = Decimal(0)
    order_without_lead.save()

    got = tasks.push_order_to_amocrm(order_id=order_without_lead.id)

    assert got == "not for amocrm"
    mock_chain.assert_not_called()


def test_not_push_if_there_is_already_paid_order(order_without_lead, paid_order, mock_chain):
    got = tasks.push_order_to_amocrm(order_id=order_without_lead.id)

    assert got == "not for amocrm"
    mock_chain.assert_not_called()
