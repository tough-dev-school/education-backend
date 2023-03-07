import pytest


@pytest.fixture
def record(mixer):
    return mixer.blend(
        "products.Record",
        name="Пентакли и тентакли",
        name_receipt="Предоставление доступа к записи курса «Пентакли и Тентакли»",
    )


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Авраам Соломонович", last_name="Пейзенгольц")


@pytest.fixture
def order(factory, user, record):
    return factory.order(user=user, item=record, price="100500")
