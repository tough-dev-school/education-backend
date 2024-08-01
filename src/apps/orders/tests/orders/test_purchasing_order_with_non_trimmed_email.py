import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def course(factory):
    return factory.course(slug="ruloning-oboev", price=1900)


@pytest.fixture(autouse=True)
def user_with_the_same_username_but_without_a_space_in_the_end(mixer):
    user = mixer.blend("users.User", email="zaboy@gmail.com")

    return user.update(username="zaboy@gmail.com")  # workaround for make_username_truly_random(), we need particular username here


@pytest.fixture(autouse=True)
def bank(mocker):
    return mocker.patch("apps.tinkoff.bank.TinkoffBank.get_initial_payment_url", return_value="https://mocked")


@pytest.fixture
def call_purchase(api):
    return lambda **kwargs: api.post(
        "/api/v2/courses/ruloning-oboev/purchase/",
        data=kwargs,
        format="multipart",
        expected_status_code=302,
    )


@pytest.mark.parametrize(
    "email",
    [
        "zaboy@gmail.com ",
        " zaboy@gmail.com",
    ],
)
def test(call_purchase, bank, email):
    call_purchase(name="Забой Шахтёров", email=email)

    bank.assert_called_once()
