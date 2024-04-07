import pytest

from apps.tinkoff.bank import TinkoffBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def tinkoff(order):
    return lambda **kwargs: TinkoffBank(order=order, **kwargs)


def test_default_success_url(tinkoff):
    client = tinkoff()

    assert client.success_url == "https://front.tst.hst/success/"


def test_custom_success_url(tinkoff):
    client = tinkoff(success_url="https://test/ok")

    assert client.success_url == "https://test/ok"


def test_default_fail_url(tinkoff):
    client = tinkoff()

    assert client.fail_url == "https://front.tst.hst/error/?code=banking"


def test_custom_fail_url(tinkoff):
    client = tinkoff(fail_url="https://test/fail")

    assert client.fail_url == "https://test/fail"
