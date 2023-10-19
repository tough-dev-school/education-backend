import pytest

from apps.mailing.tasks import send_mail

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def init(mocker):
    return mocker.patch("apps.mailing.tasks.Owl")


@pytest.fixture
def call(mocker):
    return mocker.patch("apps.mailing.tasks.Owl.__call__")


ARGS = dict(
    to=["f@f213.in"],
    template_id=100500,
    subject="Графиня изменившимся лицом бежит пруду",
    ctx={
        "a": "testing",
    },
    disable_antispam=False,
)


def test_init(init):
    send_mail(**ARGS)

    init.assert_called_once_with(**ARGS)


def test_call(call):
    send_mail(**ARGS)

    call.assert_called_once()
