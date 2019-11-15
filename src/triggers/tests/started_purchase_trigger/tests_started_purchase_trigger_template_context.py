import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def fix_frontend_url(settings):
    settings.FRONTEND_URL = 'https://frontend'


def test(trigger):
    ctx = trigger.get_template_context()

    assert ctx['item'] == 'Билет на курс кройки и шитья'
    assert ctx['item_lower'] == 'билет на курс кройки и шитья'
    assert ctx['firstname'] == 'Камаз'
    assert 'https://frontend' in ctx['item_url']
