import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def study(order):
    return order.study


@pytest.fixture
def order(course, user, factory):
    return factory.order(item=course, user=user, is_paid=True)


@pytest.fixture
def chain(mixer, course):
    return mixer.blend("chains.Chain", course=course, sending_is_active=True, archived=False)


@pytest.fixture
def parent_message(mixer, chain):
    return mixer.blend("chains.Message", parent=None, chain=chain)


@pytest.fixture
def progress(parent_message, mixer, study):
    return mixer.blend("chains.Progress", message=parent_message, study=study)


@pytest.fixture
def message(mixer, chain, parent_message):
    return mixer.blend("chains.Message", parent=parent_message, chain=chain, delay=3)
