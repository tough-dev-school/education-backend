import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _freeze_frontend_url(settings):
    settings.FRONTEND_URL = 'https://frontend'


@pytest.fixture
def record(mixer, course):
    return mixer.blend('products.Record', course=course)


@pytest.fixture
def bundle(mixer, course):
    bundle = mixer.blend('products.Bundle')
    bundle.courses.add(course)

    return bundle


def test(trigger):
    ctx = trigger.get_template_context()

    assert ctx['item'] == 'Билет на курс кройки и шитья'
    assert ctx['item_lower'] == 'билет на курс кройки и шитья'
    assert ctx['firstname'] == 'Камаз'
    assert 'https://frontend' in ctx['item_url']


def test_with_record(trigger, record):
    trigger.order.set_item(record)
    trigger.order.save()

    ctx = trigger.get_template_context()

    assert 'https://frontend' in ctx['item_url']


def test_with_bundle(trigger, bundle):
    trigger.order.set_item(bundle)
    trigger.order.save()

    ctx = trigger.get_template_context()

    assert 'https://frontend' in ctx['item_url']
