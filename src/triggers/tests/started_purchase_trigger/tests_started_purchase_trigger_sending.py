import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_condition_to_always_true(mocker, trigger):
    return mocker.patch.object(trigger, "condition", return_value=True)


def test(trigger, send_mail):
    trigger()

    args = send_mail.call_args[1]

    assert args["ctx"]["firstname"] == "Камаз"
    assert args["to"] == "kamaz.otkhodov@gmail.com"


def test_only_once(trigger, send_mail):
    for _ in range(2):
        trigger()

    send_mail.assert_called_once()
