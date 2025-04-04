import pytest


@pytest.fixture
def course(factory):
    return factory.course()


@pytest.fixture
def another_course(factory):
    return factory.course()


@pytest.fixture
def module(factory, course):
    return factory.module(course=course)


@pytest.fixture
def another_module(factory, course):
    return factory.module(course=course)


@pytest.fixture(autouse=True)
def lesson(factory, module):
    return factory.lesson(module=module)


@pytest.fixture(autouse=True)
def purchase(factory, api, course):
    return factory.order(user=api.user, item=course, is_paid=True)


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()
