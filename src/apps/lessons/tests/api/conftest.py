import pytest


@pytest.fixture
def course(factory):
    return factory.course()


@pytest.fixture
def another_course(factory):
    return factory.course()


@pytest.fixture(autouse=True)
def lesson(factory, course):
    return factory.lesson(course=course)


@pytest.fixture
def another_lesson(factory, course):
    return factory.lesson(course=course)


@pytest.fixture(autouse=True)
def purchase(factory, api, course):
    return factory.order(user=api.user, item=course, is_paid=True)


@pytest.fixture
def _no_purchase(purchase):
    purchase.unship()
