import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def send(mocker):
    return mocker.patch('app.tasks.send_mail.delay')


@pytest.fixture(autouse=True)
def set_condition_to_always_true(mocker, trigger):
    return mocker.patch.object(trigger, 'condition', return_value=True)


def test(trigger, send):
    trigger()

    args = send.call_args[1]

    assert args['ctx']['firstname'] == 'Камаз'
    assert args['to'] == 'kamaz.otkhodov@gmail.com'


def test_only_once(trigger, send):
    for _ in range(0, 2):
        trigger()

    send.assert_called_once()
