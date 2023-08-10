import pytest

from users.services import UserCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mock_update_user_chain(mocker):
    return mocker.patch("users.services.user_creator.chain")


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("users.tasks.rebuild_tags.si")


@pytest.fixture
def mock_push_customer(mocker):
    return mocker.patch("amocrm.tasks.push_user_to_amocrm.si")


def test_call_create_user_celery_chain_if_subscribe_and_amocrm_enabled(mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    user = UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com", subscribe=True)()

    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=user.id, subscribe=True),
        mock_push_customer(user_id=user.id),
    )


def test_call_push_customer_if_not_subscribe_and_amocrm_enabled(mock_push_customer, settings, mock_update_user_chain, mock_rebuild_tags):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    user = UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com")()


    mock_update_user_chain.assert_called_once_with(
        mock_rebuild_tags(student_id=user.id, subscribe=False),
        mock_push_customer(user_id=user.id),
    )


def test_not_call_push_customer_if_not_subscribe_and_amocrm_disabled(mock_update_user_chain, mock_rebuild_tags, mock_push_customer):
    UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com")()

    mock_update_user_chain.assert_not_called()
    mock_rebuild_tags.assert_not_called()
    mock_push_customer.assert_not_called()


def test_not_call_push_customer_if_not_subscribe_and_not_push_to_amocrm(mock_update_user_chain, mock_rebuild_tags, mock_push_customer, settings):
    settings.AMOCRM_BASE_URL = "https://amo.amo.amo"

    UserCreator(name="Рулон Обоев", email="rulon.oboev@gmail.com", push_to_amocrm=False)()

    mock_update_user_chain.assert_not_called()
    mock_rebuild_tags.assert_not_called()
    mock_push_customer.assert_not_called()
