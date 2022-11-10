import pytest


@pytest.fixture(autouse=True)
def _set_tinkoff_business_prod_mode(settings):
    settings.TINKOFF_BUSINESS_DEMO_MODE = False
    settings.TINKOFF_BUSINESS_TOKEN = 'se7ret'
