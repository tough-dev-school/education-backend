from functools import partial

import pytest

from apps.mailing.owl import Owl

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_email(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def owl():
    return partial(
        Owl,
        to="f@f213.in",
        template_id=100500,
    )
