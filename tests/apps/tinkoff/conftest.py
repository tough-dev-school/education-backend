import json
import pytest

from respx import MockRouter


@pytest.fixture
def course(factory):
    return factory.course(
        name="Пентакли и тентакли",
        name_receipt="Предоставление доступа к записи курса «Пентакли и Тентакли»",
    )


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Авраам Соломонович", last_name="Пейзенгольц", email="avraam-the-god@gmail.com")


@pytest.fixture
def order(factory, user, course):
    return factory.order(user=user, item=course, price="100500")


@pytest.fixture
def retrieve_request_json(respx_mock: MockRouter):
    return lambda: json.loads(respx_mock.calls.last.request.content)
