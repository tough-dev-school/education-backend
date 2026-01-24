import pytest

from apps.homework.models import AnswerAttachment

pytestmark = [pytest.mark.django_db]


def test_attachment_is_created(api, factory):
    api.post(
        "/api/v2/homework/answers/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
    )

    created = AnswerAttachment.objects.order_by("-created").first()

    assert created.file.path.endswith(".pdf")


def test_response(api, factory):
    response = api.post(
        "/api/v2/homework/answers/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
    )

    assert "testserver/media/homework/attachments" in response["file"], "Contains upload folder"
    assert response["file"].endswith(".pdf"), "Contains given extension"


def test_no_anon(anon, factory):
    anon.post(
        "/api/v2/homework/answers/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
        expected_status_code=401,
    )


def test_non_pdf_rejected(api, factory):
    api.post(
        "/api/v2/homework/answers/attachment/",
        {
            "file": factory.image(),
        },
        format="multipart",
        expected_status_code=400,
    )
