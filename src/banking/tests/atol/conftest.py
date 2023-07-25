import pytest

from banking.atol.client import AtolClient

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _configure_atol(settings):
    settings.ATOL_LOGIN = "zer0cool"
    settings.ATOL_PASSWORD = "love"
    settings.ATOL_GROUP_CODE = "group_code_19315"
    settings.ATOL_PAYMENT_ADDRESS = "Планета Алдераан, Звезда Смерти, док 2204"
    settings.VAT_ID = "71100500"
    settings.RECEIPTS_EMAIL = "receipts@tough-dev.school"


@pytest.fixture(autouse=True)
def _configure_webhooks(settings):
    settings.ABSOLUTE_HOST = "https://atol.host"
    settings.ATOL_WEBHOOK_SALT = "SECRET-SALT"


@pytest.fixture
def atol(order):
    return AtolClient(order=order)


@pytest.fixture
def post(mocker):
    return mocker.patch("banking.atol.client.AtolClient.post")


@pytest.fixture
def course(factory):
    return factory.course(
        name="Пентакли и тентакли",
        name_receipt="Предоставление доступа к записи курса «Пентакли и Тентакли»",
    )


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Авраам Соломонович", last_name="Пейзенгольц", email="abraham@gmail.com")


@pytest.fixture
def order(factory, user, course):
    return factory.order(user=user, item=course, price="100500")
