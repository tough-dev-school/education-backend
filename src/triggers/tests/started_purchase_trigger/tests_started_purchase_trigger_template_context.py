import pytest

pytestmark = [pytest.mark.django_db]


def test(trigger):
    ctx = trigger.get_template_context()

    assert ctx["item"] == "Билет на курс кройки и шитья"
    assert ctx["item_lower"] == "билет на курс кройки и шитья"
    assert ctx["firstname"] == "Камаз"
