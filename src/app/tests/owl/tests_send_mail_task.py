import pytest

from app.tasks import send_mail

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_email(settings):
    settings.EMAIL_ENABLED = True


@pytest.fixture
def owl(mocker):
    return mocker.patch('app.tasks.mail.Owl')


@pytest.fixture
def send(mocker):
    return mocker.patch('app.tasks.mail.Owl.send')


ARGS = dict(
    to=['f@f213.in'],
    template_id=100500,
    subject='Графиня изменившимся лицом бежит пруду',
    ctx={
        'a': 'testing',
    },
    disable_antispam=False,
)


def test_init(owl):
    send_mail(**ARGS)

    owl.assert_called_once_with(**ARGS)


def test_send(send):
    send_mail(**ARGS)

    send.assert_called_once()
