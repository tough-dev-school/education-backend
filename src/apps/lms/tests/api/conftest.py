import pytest


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture
def course(factory):
    return factory.course()


@pytest.fixture
def another_course(factory):
    return factory.course()


@pytest.fixture
def module(factory, course):
    return factory.module(
        course=course,
        start_date="1972-12-01 15:30+03:00",  # to avoid hiding upon select
        name="Первая неделя",
        description="Самая важная неделя",
        text="Текст модуля",
    )


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
