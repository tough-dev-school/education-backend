import pytest

from apps.mailing.owl import Owl

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _freeze_sender(settings):
    settings.DEFAULT_FROM_EMAIL = "Jesus Christ <me@christ.com>"


@pytest.mark.parametrize(
    ("ctx", "expected"),
    [
        (None, {}),
        ({"a": None, "b": "c"}, {"b": "c"}),
        ({"a": "b"}, {"a": "b"}),
    ],
)
def test_ctx_dict(ctx, expected):
    owl = Owl("test@test.org", 100500, ctx=ctx)

    message = owl.get_message(owl.default_configuration)

    assert message.merge_global_data == expected


def test_subject():
    owl = Owl("test@test.org", 100500, subject="Some email subject")

    assert owl.subject == "Some email subject"


def test_omitted_subject():
    owl = Owl("test@test.org", 100500)

    assert owl.subject == ""


def test_msg_params():
    owl = Owl("test@test.org", 100500, subject="Some email subject", ctx={"a": "b"})

    message = owl.get_message(owl.default_configuration)

    assert message.from_email == "Jesus Christ <me@christ.com>"
    assert message.merge_global_data == {"a": "b"}
    assert message.template_id == 100500
    assert message.subject == "Some email subject"
