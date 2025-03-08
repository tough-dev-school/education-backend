import pytest


@pytest.fixture(autouse=True)
def _set_default_currency_rate(request, mocker):
    if "no_default_currency_rate" in request.keywords:
        return
    mocker.patch("apps.tinkoff.bank.Bank.get_currency_rate", return_value=1)
