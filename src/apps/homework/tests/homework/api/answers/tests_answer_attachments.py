import pytest

pytestmark = [pytest.mark.django_db]


def test_answer_includes_attachments(api, factory, user):
    question = factory.question()
    answer = factory.answer(question=question, author=user)
    factory.answer_attachment(answer=answer, author=user)

    response = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert "attachments" in response
    assert len(response["attachments"]) == 1
    assert response["attachments"][0]["file"].endswith(".pdf")


def test_answer_with_no_attachments(api, factory, user):
    question = factory.question()
    answer = factory.answer(question=question, author=user)

    response = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert response["attachments"] == []


def test_answer_with_multiple_attachments(api, factory, user):
    question = factory.question()
    answer = factory.answer(question=question, author=user)
    factory.answer_attachment(answer=answer, author=user)
    factory.answer_attachment(answer=answer, author=user)

    response = api.get(f"/api/v2/homework/answers/{answer.slug}/")

    assert len(response["attachments"]) == 2
