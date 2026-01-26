import pytest

from apps.homework.models import AnswerAttachment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def answer(factory, user):
    question = factory.question()
    return factory.answer(question=question, author=user)


def test_attachment_is_created(api, factory, answer):
    api.post(
        f"/api/v2/homework/answers/{answer.slug}/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
    )

    created = AnswerAttachment.objects.order_by("-created").first()

    assert created.file.path.endswith(".pdf")
    assert created.answer == answer


def test_response(api, factory, answer):
    response = api.post(
        f"/api/v2/homework/answers/{answer.slug}/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
    )

    assert "testserver/media/homework/attachments" in response["file"], "Contains upload folder"
    assert response["file"].endswith(".pdf"), "Contains given extension"


def test_no_anon(anon, factory, answer):
    anon.post(
        f"/api/v2/homework/answers/{answer.slug}/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
        expected_status_code=401,
    )


def test_non_pdf_rejected(api, factory, answer):
    api.post(
        f"/api/v2/homework/answers/{answer.slug}/attachment/",
        {
            "file": factory.image(),
        },
        format="multipart",
        expected_status_code=400,
    )


def test_answer_not_found(api, factory):
    api.post(
        "/api/v2/homework/answers/00000000-0000-0000-0000-000000000000/attachment/",
        {
            "file": factory.pdf(),
        },
        format="multipart",
        expected_status_code=404,
    )
