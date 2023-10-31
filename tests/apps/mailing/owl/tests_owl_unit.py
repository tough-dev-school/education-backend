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
    assert owl.msg.merge_global_data == expected


def test_subject():
    owl = Owl("test@test.org", 100500, subject="Some email subject")

    assert owl.subject == "Some email subject"


def test_omitted_subject():
    owl = Owl("test@test.org", 100500)

    assert owl.subject == ""


def test_msg_params():
    owl = Owl("test@test.org", 100500, subject="Some email subject", ctx={"a": "b"})

    assert owl.msg.from_email == "Jesus Christ <me@christ.com>"
    assert owl.msg.merge_global_data == {"a": "b"}
    assert owl.msg.template_id == 100500
    assert owl.msg.subject == "Some email subject"
