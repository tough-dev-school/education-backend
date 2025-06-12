import pytest

from apps.homework.models import AnswerImage

pytestmark = [pytest.mark.django_db]


def test_image_is_created(api, factory):
    api.post(
        "/api/v2/homework/answers/image/",
        {
            "image": factory.image(),
        },
        format="multipart",
    )

    created = AnswerImage.objects.order_by("-created").first()

    assert created.image.path.endswith(".gif")


def test_response(api, factory):
    response = api.post(
        "/api/v2/homework/answers/image/",
        {
            "image": factory.image(),
        },
        format="multipart",
    )

    assert "testserver/media/homework/answers" in response["image"], "Contains upload folder"
    assert response["image"].endswith(".gif"), "Contains given extension"


def test_no_anon(anon, factory):
    anon.post(
        "/api/v2/homework/answers/image/",
        {
            "image": factory.image(),
        },
        format="multipart",
        expected_status_code=401,
    )
